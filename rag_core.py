import hashlib
import logging
import os
import re
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from documents import Document, SEED_DOCUMENTS
from llm_provider import get_provider

logger = logging.getLogger("rbac-rag")

# Gemini embeddings score unrelated documents around 0.5-0.67, so it needs a higher bar than Titan.
_DEFAULT_THRESHOLD = "0.70" if os.getenv("LLM_PROVIDER", "").lower() == "gemini" else "0.35"
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", _DEFAULT_THRESHOLD))

# Global reference to vector store
_vector_store: List[Document] = []
_llm = None
_initialized = False


def set_vector_store(vector_store: List[Document]):
    """Set the global vector store reference."""
    global _vector_store
    _vector_store = vector_store


def set_llm(llm):
    """Set the global LLM reference."""
    global _llm
    _llm = llm


def _get_llm():
    """Return the LLM provider, creating it on first use outside mock mode."""
    global _llm
    if _llm is None and os.getenv("SKIP_INDEXING") != "1":
        _llm = get_provider()
    return _llm


def get_embedding(text: str) -> List[float]:
    """Get embedding from configured LLM provider."""
    if os.getenv("SKIP_INDEXING") == "1":
        import hashlib
        hash_val = hashlib.md5(text.encode()).digest()
        return [float(b) / 128.0 for b in hash_val] + [0.0] * (1024 - len(hash_val))
    return _get_llm().get_embedding(text)


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

    if os.getenv("SKIP_INDEXING") == "1":
        if not context_blocks:
            answer = "I do not have enough authorized information to answer that question."
        else:
            top_doc = retrieved_docs[0][0]
            answer = f"Based on {top_doc.doc_id} ({top_doc.title}): {top_doc.content}"
        return answer, 0, 0, 0.0

    answer, input_tokens, output_tokens, cost_usd = _get_llm().generate_answer(
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


EMBEDDINGS_DIR = Path(__file__).parent / "embeddings"


def _doc_text(doc: Document) -> str:
    return f"{doc.title}\n{doc.content}"


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def embedding_cache_path(provider_name: str) -> Path:
    return EMBEDDINGS_DIR / f"{provider_name}.npz"


def load_embedding_cache(provider_name: str, model: str) -> Dict[str, Tuple[str, np.ndarray]]:
    """Return {doc_id: (text_hash, vector)} from the precomputed file, or {} if missing or built with another model."""
    path = embedding_cache_path(provider_name)
    if not path.exists():
        return {}
    with np.load(path) as data:
        if str(data["model"]) != model:
            logger.warning("Ignoring %s: built with %s, current model is %s", path.name, data["model"], model)
            return {}
        return {
            str(doc_id): (str(text_hash), vec)
            for doc_id, text_hash, vec in zip(data["ids"], data["hashes"], data["vectors"])
        }


def save_embedding_cache(provider_name: str, model: str, docs: List[Document]) -> Path:
    """Write the embeddings already attached to docs so later startups can skip the API calls."""
    EMBEDDINGS_DIR.mkdir(exist_ok=True)
    path = embedding_cache_path(provider_name)
    np.savez_compressed(
        path,
        model=model,
        ids=np.array([d.doc_id for d in docs]),
        hashes=np.array([_text_hash(_doc_text(d)) for d in docs]),
        vectors=np.array([d.embedding for d in docs], dtype=np.float32),
    )
    return path


def index_documents(docs: List[Document]) -> List[Document]:
    """Attach an embedding to each doc, reusing the precomputed cache for docs whose text hasn't changed."""
    cache: Dict[str, Tuple[str, np.ndarray]] = {}
    if os.getenv("SKIP_INDEXING") != "1":
        llm = _get_llm()
        cache = load_embedding_cache(os.getenv("LLM_PROVIDER", "bedrock").lower(), llm.embed_model_name)

    reused = 0
    for doc in docs:
        text = _doc_text(doc)
        cached = cache.get(doc.doc_id)
        if cached and cached[0] == _text_hash(text):
            doc.embedding = cached[1].tolist()
            reused += 1
        else:
            doc.embedding = get_embedding(text)
    logger.info("Indexed %d documents (%d from precomputed cache, %d embedded)", len(docs), reused, len(docs) - reused)
    return docs


_init_lock = threading.Lock()


def _ensure_initialized():
    """Lazy initialization of vector store on first access."""
    global _initialized
    if _initialized or _vector_store:
        return
    with _init_lock:
        if _initialized or _vector_store:
            return
        logger.info(f"Lazy initializing vector store with {len(SEED_DOCUMENTS)} documents...")
        # Build fully before publishing so a concurrent search never sees a half-built index.
        _vector_store.extend(index_documents(list(SEED_DOCUMENTS)))
        _initialized = True
        logger.info(f"✅ Vector store initialized: {len(_vector_store)} documents")


_STOPWORDS = {
    "the", "and", "for", "are", "what", "how", "who", "when", "where", "why", "does", "did", "can",
    "our", "your", "you", "with", "from", "that", "this", "have", "has", "was", "were", "will",
    "about", "into", "tell", "give", "show", "please", "need", "know", "any", "all", "get",
    "policy", "policies", "company", "employee", "employees", "work", "per", "its", "not",
}


def _tokens(text: str) -> set:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w.rstrip("s") if len(w) > 3 else w for w in words if len(w) > 2 and w not in _STOPWORDS}


MOCK_MIN_COVERAGE = float(os.getenv("MOCK_MIN_COVERAGE", "0.5"))


def _keyword_search(query: str, pool: List[Document], top_k: int) -> List[tuple[Document, float]]:
    """Mock-mode retrieval: rank authorized docs by keyword overlap; abstain below MOCK_MIN_COVERAGE of the question's keywords."""
    q = _tokens(query)
    if not q:
        return []
    scored = []
    for doc in pool:
        title_tokens, content_tokens = _tokens(doc.title), _tokens(doc.content)
        if len(q & (title_tokens | content_tokens)) / len(q) < MOCK_MIN_COVERAGE:
            continue
        hits = len(q & content_tokens) + len(q & title_tokens)
        scored.append((doc, min(1.0, hits / (2 * len(q)))))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_k]


def search_authorized_docs(query: str, user_role: str, top_k: int) -> List[tuple[Document, float]]:
    """
    Filter by `user_role` BEFORE computing vector similarity.
    In mock mode, ranks authorized documents by keyword overlap instead of embeddings.
    """
    _ensure_initialized()
    logger.info(f"Search: query='{query}', role='{user_role}', VECTOR_STORE size={len(_vector_store)}")

    authorized_pool = [doc for doc in _vector_store if user_role in doc.allowed_roles]
    logger.info(f"Authorized docs for {user_role}: {len(authorized_pool)} found")

    if not authorized_pool:
        logger.info(f"No authorized docs found for {user_role}")
        return []

    if os.getenv("SKIP_INDEXING") == "1":
        result = _keyword_search(query, authorized_pool, top_k)
        logger.info(f"Mock mode: returning {len(result)} documents")
        return result

    query_vec = np.array(get_embedding(query))

    scored_docs = []
    for doc in authorized_pool:
        doc_vec = np.array(doc.embedding)
        score = float(np.dot(query_vec, doc_vec))
        if score >= SIMILARITY_THRESHOLD:
            scored_docs.append((doc, score))

    scored_docs.sort(key=lambda pair: pair[1], reverse=True)
    return scored_docs[:top_k]
