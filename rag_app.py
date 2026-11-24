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
from documents import Document, SEED_DOCUMENTS
from rag_core import generate_grounded_answer_with_usage, search_authorized_docs, set_vector_store, set_llm, get_embedding

# ---------------------------------------------------------------------------
# 1. CONFIGURATION & LOGGING
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("rbac-rag")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "bedrock").lower()
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
        logger.warning(f"⚠️ Failed to initialize LLM provider: {e}. Running in mock mode.")
        llm = None
        os.environ["SKIP_INDEXING"] = "1"

# Set LLM for rag_core module
set_llm(llm)

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


VECTOR_STORE: List[Document] = []


# ---------------------------------------------------------------------------
# 4. LIFECYCLE & API ENDPOINTS
# ---------------------------------------------------------------------------
@app.on_event("startup")
def index_seed_documents():
    """Embeds the seed documents once when the server boots."""
    logger.info("Indexing %d enterprise documents into vector store...", len(SEED_DOCUMENTS))
    VECTOR_STORE.clear()
    for doc in SEED_DOCUMENTS:
        doc.embedding = get_embedding(f"{doc.title}\n{doc.content}")
        VECTOR_STORE.append(doc)

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
    return {"status": "ok", "indexed_docs": len(VECTOR_STORE), "provider": LLM_PROVIDER}


@app.get("/debug/vector-store")
def debug_vector_store():
    """Debug endpoint to check what's in VECTOR_STORE"""
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
