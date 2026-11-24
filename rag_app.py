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

# ---------------------------------------------------------------------------
# 1. CONFIGURATION & LOGGING
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("rbac-rag")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "bedrock").lower()
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize the LLM provider
try:
    llm = get_provider()
    logger.info(f"✅ Using LLM provider: {LLM_PROVIDER}")
except Exception as e:
    logger.warning(f"⚠️ Failed to initialize LLM provider: {e}. Running in mock mode.")
    llm = None
    os.environ["SKIP_INDEXING"] = "1"

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
class Document(BaseModel):
    doc_id: str
    title: str
    content: str
    allowed_roles: List[str]
    embedding: Optional[List[float]] = None


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="The user's natural language question.")
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


# ---------------------------------------------------------------------------
# 3. SIMULATED ENTERPRISE KNOWLEDGE BASE (5 POLICY DOCUMENTS)
# ---------------------------------------------------------------------------
SEED_DOCUMENTS: List[Document] = [
    Document(
        doc_id="DOC-ALL-01",
        title="2026 Company Holiday & PTO Policy",
        content=(
            "Company offices are closed on New Year's Day, Memorial Day, July 4th, Labor Day, "
            "Thanksgiving (Thu-Fri), and Dec 24-25. Full-time employees accrue 20 days of PTO per year "
            "and may carry over up to 5 unused days into the next calendar year. PTO requests over 5 "
            "consecutive days require manager approval at least 2 weeks in advance."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-SEC-01",
        title="Enterprise Data Security, PII & Remote Work Policy",
        content=(
            "All corporate laptops must enforce FileVault or BitLocker full-disk encryption and hardware MFA. "
            "Employees working remotely must connect through the corporate WireGuard VPN before accessing "
            "internal staging or production networks. Customer PII (SSNs, emails, medical or financial records) "
            "must NEVER be pasted into unapproved public AI tools. Suspected data breaches or lost devices "
            "must be reported to security@company.internal within 2 hours."
        ),
        allowed_roles=["employee", "engineering", "hr", "executive"],
    ),
    Document(
        doc_id="DOC-ENG-01",
        title="Production Incident Runbook (SEV-1)",
        content=(
            "For SEV-1 production outages, page the on-call SRE via PagerDuty within 5 minutes, "
            "open #inc-war-room in Slack, assign an Incident Commander, and freeze all CI/CD deploys "
            "until root cause is mitigated. Post-incident blameless postmortems are due within 48 hours "
            "and must include a corrective action Jira ticket."
        ),
        allowed_roles=["engineering", "executive"],
    ),
    Document(
        doc_id="DOC-HR-01",
        title="2026 Engineering Compensation Bands (Confidential)",
        content=(
            "L4 Software Engineer base salary band is $145,000-$170,000. "
            "L5 Senior Engineer base salary band is $175,000-$210,000. "
            "L6 Staff Engineer base salary band is $215,000-$255,000. "
            "Annual performance bonus target is 15% across all engineering levels. "
            "Merit reviews occur every March."
        ),
        allowed_roles=["hr", "executive"],
    ),
    Document(
        doc_id="DOC-EXEC-01",
        title="Project Titan Acquisition Memo (Restricted)",
        content=(
            "Board approval is pending for the $42M acquisition of CloudScale Analytics, "
            "targeted to close in Q1 2027. Deal lead is CFO Elena Vance. "
            "This memo is strictly confidential under NDA until public SEC filing."
        ),
        allowed_roles=["executive"],
    ),
]

VECTOR_STORE: List[Document] = []


# ---------------------------------------------------------------------------
# 4. AMAZON BEDROCK HELPERS (EMBEDDINGS & GENERATION)
# ---------------------------------------------------------------------------
def get_embedding(text: str) -> List[float]:
    """Get embedding from configured LLM provider."""
    if llm is None or os.getenv("SKIP_INDEXING") == "1":
        # Mock embedding for testing
        import hashlib
        hash_val = hashlib.md5(text.encode()).digest()
        return [float(b) / 128.0 for b in hash_val] + [0.0] * (1024 - len(hash_val))

    return llm.get_embedding(text)


def generate_grounded_answer_with_usage(
    question: str,
    retrieved_docs: List[tuple[Document, float]],
    model_id: Optional[str] = None,
) -> tuple[str, int, int, float]:
    """
    Generate grounded answer using configured LLM provider.
    Returns (answer_text, input_tokens, output_tokens, estimated_cost_usd).
    """
    context_blocks = [
        f"[{doc.doc_id}] ({doc.title}):\n{doc.content}"
        for doc, _ in retrieved_docs
    ]
    context_str = "\n\n".join(context_blocks)

    system_prompt = (
        "You are a secure enterprise assistant. Answer the user's question using ONLY "
        "the provided context blocks. Cite your sources inline using the bracketed ID, e.g. [DOC-ENG-01]. "
        "If the provided context does not contain the answer, respond ONLY with: "
        "'I do not have enough authorized information to answer that question.' "
        "Never guess or use outside knowledge."
    )

    # Mock mode: generate mock answer from context
    if os.getenv("SKIP_INDEXING") == "1":
        if not context_blocks:
            answer = "I do not have enough authorized information to answer that question."
        else:
            # Use first context block as mock answer
            answer = f"Based on {retrieved_docs[0][0].doc_id}: {retrieved_docs[0][0].content[:200]}..."
        return answer, 0, 0, 0.0

    # Real mode: use LLM provider
    if llm is None:
        answer = "I do not have enough authorized information to answer that question."
        return answer, 0, 0, 0.0

    answer, input_tokens, output_tokens, cost_usd = llm.generate_answer(
        question=question,
        context=context_str,
        system_prompt=system_prompt,
    )
    return answer, input_tokens, output_tokens, cost_usd


def generate_grounded_answer(
    question: str,
    retrieved_docs: List[tuple[Document, float]],
    model_id: Optional[str] = None,
) -> str:
    """Backwards-compatible helper returning only the grounded answer string."""
    answer, _, _, _ = generate_grounded_answer_with_usage(question, retrieved_docs, model_id=model_id)
    return answer


# ---------------------------------------------------------------------------
# 5. PRE-RETRIEVAL RBAC VECTOR SEARCH (CORE SECURITY BOUNDARY)
# ---------------------------------------------------------------------------
def search_authorized_docs(query: str, user_role: str, top_k: int) -> List[tuple[Document, float]]:
    """
    Filter by `user_role` BEFORE computing vector similarity.
    In mock mode, returns all authorized documents (no similarity threshold).
    """
    authorized_pool = [doc for doc in VECTOR_STORE if user_role in doc.allowed_roles]
    if not authorized_pool:
        return []

    # Mock mode: return all authorized documents for demo
    if os.getenv("SKIP_INDEXING") == "1":
        return [(doc, 1.0) for doc in authorized_pool[:top_k]]

    query_vec = np.array(get_embedding(query))

    scored_docs = []
    for doc in authorized_pool:
        doc_vec = np.array(doc.embedding)
        score = float(np.dot(query_vec, doc_vec))
        if score >= SIMILARITY_THRESHOLD:
            scored_docs.append((doc, score))

    scored_docs.sort(key=lambda pair: pair[1], reverse=True)
    return scored_docs[:top_k]


# ---------------------------------------------------------------------------
# 6. LIFECYCLE & API ENDPOINTS
# ---------------------------------------------------------------------------
@app.on_event("startup")
def index_seed_documents():
    """Embeds the 5 seed documents once when the server boots."""
    logger.info("Indexing %d enterprise documents into vector store...", len(SEED_DOCUMENTS))
    VECTOR_STORE.clear()
    for doc in SEED_DOCUMENTS:
        doc.embedding = get_embedding(f"{doc.title}\n{doc.content}")
        VECTOR_STORE.append(doc)

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
    return {"status": "ok", "indexed_docs": len(VECTOR_STORE), "provider": LLM_PROVIDER}


@app.post("/query", response_model=QueryResponse)
def query_knowledge_base(
    req: QueryRequest,
    x_user_role: str = Header(..., description="Simulated role: employee | engineering | hr | executive"),
):
    start = time.perf_counter()
    valid_roles = {"employee", "engineering", "hr", "executive"}
    role = x_user_role.strip().lower()
    if role not in valid_roles:
        raise HTTPException(status_code=403, detail=f"Invalid role '{role}'. Must be one of {valid_roles}.")

    logger.info("AUDIT | role=%s | question=%r", role, req.question)

    matches = search_authorized_docs(req.question, user_role=role, top_k=req.top_k)

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

    answer, in_tok, out_tok, cost_usd = generate_grounded_answer_with_usage(req.question, matches)
    latency_ms = int((time.perf_counter() - start) * 1000)

    citations = [
        Citation(
            doc_id=doc.doc_id,
            title=doc.title,
            similarity_score=round(score, 3),
            snippet=doc.content,
        )
        for doc, score in matches
    ]
    retrieved_contexts = [doc.content for doc, _ in matches]

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
