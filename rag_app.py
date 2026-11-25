"""
FastAPI web API for the permission-aware RAG assistant.

REQUEST LIFECYCLE for POST /query (what happens, in order):
    1. FastAPI parses the JSON body into QueryRequest and REJECTS bad input with HTTP 422.
    2. The X-User-Role header is read and checked against the four known roles (403 if unknown).
    3. search_authorized_docs()  (rag_core.py) returns only documents that role may read.
    4. No documents survive -> respond "insufficient_context" (no LLM call, so $0 and fast).
    5. Otherwise generate_grounded_answer_with_usage() asks the LLM to answer from those documents.
    6. We return the answer, its citations, latency, token counts and estimated cost.
"""
import json
import logging
import os
import time
from pathlib import Path
from typing import List, Optional

import numpy as np
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from llm_provider import get_provider
from documents import Document, SEED_DOCUMENTS, SAMPLE_QUESTIONS
from rag_core import generate_grounded_answer_with_usage, index_documents, search_authorized_docs, set_vector_store, set_llm, get_embedding

# ---------------------------------------------------------------------------
# 1. CONFIGURATION & LOGGING
# ---------------------------------------------------------------------------
# +- AWS EXAM [DVA-C02] ----------------------------------------------------------------------
# | Q: Where do this app's log lines end up when it runs on App Runner / ECS / Lambda, and which
# |    service answers "who called the Bedrock API?" versus "how is my app performing?"
# | A: Anything written to stdout/stderr (what logging.basicConfig does here) goes to CloudWATCH
# |    LOGS on App Runner and Lambda automatically; on ECS you must configure the awslogs log
# |    driver in the task definition. CloudTRAIL records AWS API calls
# |    (who/what/when/from where). CloudWatch = performance + logs + alarms; CloudTrail = audit.
# | WHY: Remember "Watch = watch the performance, Trail = audit trail". Bedrock also has an
# |    opt-in MODEL INVOCATION LOGGING feature (to CloudWatch Logs or S3) if you need the actual
# |    prompts and responses, which neither of the above records by default.
# +---------------------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("rbac-rag")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "bedrock").lower()
# NOTE: AWS_REGION is read here but NOT used anywhere in this file. BedrockProvider reads its own
# AWS_REGION (default us-east-2). The two defaults disagree (us-east-1 here), so only set the env var.
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize the LLM provider (skip in mock mode)
if os.getenv("SKIP_INDEXING") == "1":
    llm = None
    logger.info("✅ Mock mode: skipping LLM provider initialization")
else:
    try:
        llm = get_provider()
        logger.info(f"✅ Using LLM provider: {LLM_PROVIDER}")
    except Exception as e:
        # WARNING - SILENT FALLBACK: if the provider cannot be created (missing key, bad config),
        # the app does NOT stop. It quietly flips to mock mode, so a broken live deployment can
        # look like a working demo that just answers poorly. Check this log line first when a
        # "live" deployment behaves like keyword search.
        logger.warning(f"⚠️ Failed to initialize LLM provider: {e}. Running in mock mode.")
        llm = None
        os.environ["SKIP_INDEXING"] = "1"

# Set LLM for rag_core module
set_llm(llm)

# UNUSED here: the threshold that is actually applied lives in rag_core.py (which also picks a
# higher default for Gemini). This copy is a leftover and changing it has no effect.
# Similarity floor (0.0 to 1.0). Below this score we abstain rather than hallucinate.
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))
app = FastAPI(
    title="Permission-Aware Enterprise RAG",
    description=f"Multi-provider RBAC RAG system (using {LLM_PROVIDER})",
    version="3.0.0"
)

STATIC_DIR = Path(__file__).parent / "static"


# ---------------------------------------------------------------------------
# 2. DATA MODELS (PYDANTIC SCHEMAS)
# ---------------------------------------------------------------------------
# Pydantic models are the API CONTRACT. FastAPI validates every request against them automatically,
# so malformed input never reaches the business logic. (Playwright's api-schema tests check this.)
class QueryRequest(BaseModel):
    # min_length=3 -> a 1-2 character question is rejected with HTTP 422 (Unprocessable Content).
    question: str = Field(..., min_length=3, description="The user's natural language question.")
    # How many documents to retrieve (1-10). More = more context but more input tokens = more cost.
    top_k: int = Field(default=3, ge=1, le=10)


class Citation(BaseModel):
    doc_id: str
    title: str
    similarity_score: float
    snippet: str


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    retrieved_contexts: List[str]
    user_role: str
    status: str  # "answered" | "insufficient_context"
    latency_ms: int
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float


# The in-memory "vector database" for the API process: a list of Documents that each carry their
# embedding. In production this would be a managed vector store (OpenSearch Serverless, Aurora
# pgvector, ...), because an in-memory list is lost on restart and is not shared between instances.
VECTOR_STORE: List[Document] = []


# ---------------------------------------------------------------------------
# 4. LIFECYCLE & API ENDPOINTS
# ---------------------------------------------------------------------------
@app.on_event("startup")
def index_seed_documents():
    """Embeds the seed documents once when the server boots."""
    # Runs once when uvicorn starts, BEFORE the first request. Documents get their embeddings from
    # the precomputed cache where possible (instant, free), and only new/changed ones hit the API.
    logger.info("Indexing %d enterprise documents into vector store...", len(SEED_DOCUMENTS))
    VECTOR_STORE.clear()
    VECTOR_STORE.extend(index_documents(list(SEED_DOCUMENTS)))

    # Set the vector store for rag_core module
    set_vector_store(VECTOR_STORE)

    if os.getenv("SKIP_INDEXING") == "1":
        logger.info("✅ Mock mode: %d documents pre-indexed for demo", len(VECTOR_STORE))
    else:
        logger.info("✅ Indexing complete with %s provider", LLM_PROVIDER)


@app.get("/", include_in_schema=False)
def serve_minimal_ui():
    """Serves the minimal HTML/JS test UI for fast Playwright E2E testing."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health_check():
    # +- AWS EXAM [CLF-C02 / DVA-C02] ---------------------------------------------------------
    # | Q: How does a load balancer (or App Runner / ECS) know whether to send traffic to an
    # |    instance, or replace it?
    # | A: A HEALTH CHECK: it calls an endpoint like this one; a non-200 (or timeout) marks the
    # |    instance unhealthy and it is taken out of rotation / restarted.
    # | WHY: This is how "high availability" and self-healing work in practice (ALB target group
    # |    health checks, App Runner health check, ECS task health). Keep it cheap and fast: do
    # |    NOT call Bedrock from a health check or every probe costs money.
    # | CAVEAT: "provider" below only echoes the LLM_PROVIDER env var. It does NOT prove the
    # |    provider works, and it says "bedrock" even in mock mode.
    # +-------------------------------------------------------------------------------------------
    return {"status": "ok", "indexed_docs": len(VECTOR_STORE), "provider": LLM_PROVIDER}


@app.get("/samples")
def sample_questions():
    return [
        {"category": cat, "label": label, "role": role, "question": q}
        for cat, label, role, q, _ in SAMPLE_QUESTIONS
    ]


@app.get("/debug/vector-store")
def debug_vector_store():
    """Debug endpoint to check what's in VECTOR_STORE"""
    # SECURITY NOTE: this endpoint has no authentication and lists every document id, title and
    # allowed role. Fine for a local demo; remove it or protect it before any real deployment.
    return {
        "total_docs": len(VECTOR_STORE),
        "docs": [
            {
                "doc_id": doc.doc_id,
                "title": doc.title,
                "has_embedding": doc.embedding is not None,
                "allowed_roles": doc.allowed_roles,
            }
            for doc in VECTOR_STORE
        ]
    }


@app.post("/query", response_model=QueryResponse)
def query_knowledge_base(
    req: QueryRequest,
    x_user_role: str = Header(..., description="Simulated role: employee | engineering | hr | executive"),
):
    # perf_counter is a monotonic high-resolution clock: the right tool for measuring elapsed time.
    start = time.perf_counter()
    valid_roles = {"employee", "engineering", "hr", "executive"}
    role = x_user_role.strip().lower()

    # =========================================================================================
    # +- AWS EXAM [CLF-C02 / DVA-C02] -------------------------------------------------------
    # | SECURITY WARNING: the role comes from a header the CLIENT sets. Anyone can send
    # | "X-User-Role: executive". That is acceptable for a demo of RBAC mechanics and would be
    # | a critical vulnerability in production.
    # |
    # | Q: How should the API learn who the caller is and which role they have?
    # | A: Authenticate with a real identity provider and derive the role from VERIFIED claims:
    # |    Amazon Cognito user pool (JWT) or IAM Identity Center, validated by an API Gateway
    # |    authorizer (Cognito/JWT or Lambda authorizer) or by the app verifying the token's
    # |    signature. Use IAM auth (SigV4) for service-to-service calls.
    # | WHY: Authentication (who are you?) must be proven cryptographically; never trust an
    # |    identity or permission the caller merely states. Authorization (what may you do?) is
    # |    then decided server-side from the verified identity.
    # |
    # | Q: 401 or 403 for a caller who is not allowed?
    # | A: 401 Unauthorized = not authenticated (no/invalid credentials). 403 Forbidden =
    # |    authenticated but not permitted. We return 403 for an unknown role.
    # +---------------------------------------------------------------------------------------
    # =========================================================================================
    if role not in valid_roles:
        raise HTTPException(status_code=403, detail=f"Invalid role '{role}'. Must be one of {valid_roles}.")

    # Structured "AUDIT |" lines make this log searchable (CloudWatch Logs Insights can filter on
    # them, and a metric filter could turn "result=BLOCKED" into a CloudWatch metric + alarm).
    logger.info("AUDIT | role=%s | question=%r", role, req.question)

    # STEP 1+2: RBAC filter, then similarity search (see rag_core.search_authorized_docs).
    matches = search_authorized_docs(req.question, user_role=role, top_k=req.top_k)

    # STEP 3: nothing authorized AND relevant was found. We return immediately WITHOUT calling the
    # LLM. This single response covers several different causes that look identical to the caller:
    #   (a) the role may not read the relevant document (RBAC working as designed),
    #   (b) nothing scored above the similarity threshold,
    #   (c) in mock mode, too few keywords matched.
    # An `abstain_reason` field would make these distinguishable.
    if not matches:
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.info("AUDIT | role=%s | result=BLOCKED_OR_NO_MATCH | latency_ms=%d", role, latency_ms)
        return QueryResponse(
            answer="I do not have enough authorized information to answer that question.",
            citations=[],
            retrieved_contexts=[],
            user_role=role,
            status="insufficient_context",
            latency_ms=latency_ms,
            input_tokens=0,
            output_tokens=0,
            estimated_cost_usd=0.0,
        )

    # STEP 4: documents were found, so ask the LLM to write a grounded answer from them.
    answer, in_tok, out_tok, cost_usd = generate_grounded_answer_with_usage(req.question, matches)
    latency_ms = int((time.perf_counter() - start) * 1000)

    # Citations tell the user (and the eval tests) exactly which documents the answer came from.
    citations = [
        Citation(
            doc_id=doc.doc_id,
            title=doc.title,
            similarity_score=round(score, 3),
            snippet=doc.content,
        )
        for doc, score in matches
    ]
    # The raw retrieved text is returned too: DeepEval uses it to score whether the answer is
    # FAITHFUL to its sources (the CI quality gate).
    retrieved_contexts = [doc.content for doc, _ in matches]

    # +- AWS EXAM [CLF-C02] ---------------------------------------------------------------------
    # | Q: Which Well-Architected pillar covers measuring latency/cost per request and acting on it?
    # | A: Operational Excellence (observe/monitor) with Cost Optimization (track spend).
    # | In AWS you would publish latency_ms and cost as CloudWatch custom metrics, alarm on them,
    # | trace the request with AWS X-Ray, and watch spend with AWS Budgets / Cost Explorer.
    # +-------------------------------------------------------------------------------------------
    logger.info(
        "AUDIT | role=%s | result=ANSWERED | cited=%s | latency_ms=%d | cost=$%.6f",
        role, [c.doc_id for c in citations], latency_ms, cost_usd,
    )
    return QueryResponse(
        answer=answer,
        citations=citations,
        retrieved_contexts=retrieved_contexts,
        user_role=role,
        status="answered",
        latency_ms=latency_ms,
        input_tokens=in_tok,
        output_tokens=out_tok,
        estimated_cost_usd=cost_usd,
    )
