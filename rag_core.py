"""
Retrieval + answer generation, with no FastAPI dependency (so Streamlit can import it too).

THE RAG PIPELINE IN THIS FILE (read top to bottom of a single user question):

    question + role
        |
        v
    search_authorized_docs()   1. keep ONLY documents this role may read      (RBAC, BEFORE search)
        |                      2. embed the question into a vector
        |                      3. score each allowed document by similarity
        |                      4. drop anything below SIMILARITY_THRESHOLD, keep the top_k
        v
    generate_grounded_answer_with_usage()
                               5. paste the surviving documents into the prompt
                               6. ask the LLM to answer ONLY from them and cite [DOC-IDs]

RAG = Retrieval-Augmented Generation: retrieve relevant private text, AUGMENT the prompt with it,
then GENERATE an answer. The model is never retrained.

+- AWS EXAM [CLF-C02 / DVA-C02] ---------------------------------------------------------------
| Q: A company wants a foundation model to answer questions from its internal documents. The
|    documents change daily. What is the most cost-effective, lowest-effort approach?
| A: RAG (on AWS: Knowledge Bases for Amazon Bedrock), not fine-tuning or training a model.
| WHY: Fine-tuning/continued pre-training costs compute + time and the model is stale again as
|    soon as a document changes; it also cannot tell you WHICH document an answer came from. RAG
|    only needs the new document re-embedded, supports citations, and lets you control who sees
|    what at retrieval time. (Also tested heavily on the AI Practitioner exam, AIF-C01.)
+---------------------------------------------------------------------------------------------

HOW THIS MAPS TO MANAGED AWS SERVICES (what you would use instead of hand-rolled code in prod):
    this file's _vector_store list        ->  Amazon OpenSearch Serverless, Aurora PostgreSQL with
                                              pgvector, or another vector database
    index_documents() + embeddings cache  ->  a Knowledge Base "ingestion / sync" job
    search_authorized_docs()              ->  Knowledge Bases Retrieve API with a METADATA FILTER
    generate_grounded_answer_...()        ->  RetrieveAndGenerate API (+ Bedrock Guardrails)
"""
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

# ---------------------------------------------------------------------------------------------
# Relevance floor. A document is used only if its similarity to the question is at least this.
# Below it we ABSTAIN ("I do not have enough authorized information") rather than let the model
# improvise, because improvising is how hallucinations get into answers.
#
# The right number depends on the EMBEDDING MODEL, so it is not portable:
#     Titan (Bedrock)  -> 0.35, the project's original default (from the README's case study; not
#                         re-verified end to end here because Bedrock chat is blocked on this account)
#     Gemini           -> unrelated docs score 0.5-0.67 (measured), so it needs 0.70
# Changing the embedding model means re-tuning this number against the eval set.
# ---------------------------------------------------------------------------------------------
_DEFAULT_THRESHOLD = "0.70" if os.getenv("LLM_PROVIDER", "").lower() == "gemini" else "0.35"
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", _DEFAULT_THRESHOLD))

# Module-level "singletons" shared by everything in this process. Streamlit and FastAPI each import
# this module in their OWN process, so each process has its own copy (they do not share memory).
_vector_store: List[Document] = []   # every indexed Document, each carrying its .embedding
_llm = None                          # the provider object (BedrockProvider, GeminiProvider, ...)
_initialized = False                 # True once the store has been built lazily


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
    # MOCK MODE (SKIP_INDEXING=1): no AWS/Google call at all. This fake "embedding" is just bytes of
    # an MD5 hash scaled into floats. It has NO meaning, so similarity scores from it are random.
    # That is why mock mode uses keyword matching (_keyword_search) instead of vector similarity.
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
    # Each retrieved document becomes a labelled block: "[DOC-ENG-01] (Title): full text".
    # The label is what lets the model cite its sources inline.
    context_blocks = [
        f"[{doc.doc_id}] ({doc.title}):\n{doc.content}"
        for doc, _ in retrieved_docs
    ]
    context_str = "\n\n".join(context_blocks)

    # +- AWS EXAM [CLF-C02 / DVA-C02] -----------------------------------------------------------
    # | Q: How do you keep a Bedrock-powered assistant from making things up, and from being
    # |    talked into leaking data or ignoring its rules?
    # | A: Layer the defenses: (1) ground the answer in retrieved documents, (2) instruct the model
    # |    to refuse when the context lacks the answer, (3) use BEDROCK GUARDRAILS (content filters,
    # |    prompt-attack detection, denied topics, PII masking, contextual-grounding check), and
    # |    (4) enforce access control OUTSIDE the model (see search_authorized_docs).
    # | WHY: A system prompt is only a REQUEST to the model, and prompt injection ("ignore all
    # |    previous instructions") can override it. Guardrails run as a separate managed layer
    # |    around the model, and access control in code cannot be talked around at all.
    # +-----------------------------------------------------------------------------------------
    system_prompt = (
        "You are a secure enterprise assistant. Answer the user's question using ONLY "
        "the provided context blocks. Cite your sources inline using the bracketed ID, e.g. [DOC-ENG-01]. "
        "If the provided context does not contain the answer, respond ONLY with: "
        "'I do not have enough authorized information to answer that question.' "
        "Never guess or use outside knowledge."
    )

    # MOCK MODE: no LLM is called. The "answer" is just the top document's text, so mock answers are
    # canned and cost $0 (0 tokens).
    if os.getenv("SKIP_INDEXING") == "1":
        if not context_blocks:
            answer = "I do not have enough authorized information to answer that question."
        else:
            top_doc = retrieved_docs[0][0]
            answer = f"Based on {top_doc.doc_id} ({top_doc.title}): {top_doc.content}"
        return answer, 0, 0, 0.0

    # LIVE MODE: one LLM call (Converse API on Bedrock). Returns text plus billed token counts.
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


# ---------------------------------------------------------------------------------------------
# EMBEDDING CACHE
# Embedding all 252 documents means 252 paid API calls. Documents rarely change, so we do it ONCE
# (build_embeddings.py), save the vectors to embeddings/<provider>.npz, commit that file, and load
# it at startup. Startup then makes zero embedding calls.
#
# Safety rules baked in so a stale cache can never silently serve wrong vectors:
#   * each vector is stored with a SHA-256 hash of the exact text it came from;
#   * a document whose text changed (hash mismatch) is re-embedded, nothing else is;
#   * a cache built with a DIFFERENT embedding model is ignored entirely (vectors from different
#     models live in different "spaces" and cannot be compared).
#
# +- AWS EXAM [CLF-C02] ---------------------------------------------------------------------
# | Q: Which Well-Architected pillar does "compute once, reuse many times" support?
# | A: Cost Optimization (and Performance Efficiency).
# | WHY: Paying for the same embedding repeatedly is pure waste. Same logic as caching with
# |    CloudFront / ElastiCache, or buying reserved capacity for steady workloads.
# +-------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------
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
            doc.embedding = cached[1].tolist()   # cache hit: free, instant
            reused += 1
        else:
            doc.embedding = get_embedding(text)  # cache miss: one paid API call
    logger.info("Indexed %d documents (%d from precomputed cache, %d embedded)", len(docs), reused, len(docs) - reused)
    return docs


_init_lock = threading.Lock()


def _ensure_initialized():
    """Lazy initialization of vector store on first access."""
    global _initialized
    # Fast path: already built, nothing to do (no lock taken, so normal requests stay fast).
    if _initialized or _vector_store:
        return
    # Slow path. The lock stops two simultaneous first requests (e.g. two Streamlit sessions) from
    # both building the index. The second one waits, then sees it is done and returns.
    with _init_lock:
        if _initialized or _vector_store:   # re-check: another thread may have finished meanwhile
            return
        logger.info(f"Lazy initializing vector store with {len(SEED_DOCUMENTS)} documents...")
        # Build fully before publishing so a concurrent search never sees a half-built index.
        _vector_store.extend(index_documents(list(SEED_DOCUMENTS)))
        _initialized = True
        logger.info(f"✅ Vector store initialized: {len(_vector_store)} documents")


# ---------------------------------------------------------------------------------------------
# MOCK-MODE KEYWORD SEARCH (used only when SKIP_INDEXING=1)
# Because mock mode has no real embeddings, it ranks documents by how many of the question's
# important words appear in them. This is much cruder than vector search: it can't understand that
# "run book" and "runbook" mean the same thing, and a typo matches nothing. That is why mock mode
# abstains more often. It exists so the app can be demoed and tested at $0 with no cloud account.
# ---------------------------------------------------------------------------------------------
_STOPWORDS = {
    "the", "and", "for", "are", "what", "how", "who", "when", "where", "why", "does", "did", "can",
    "our", "your", "you", "with", "from", "that", "this", "have", "has", "was", "were", "will",
    "about", "into", "tell", "give", "show", "please", "need", "know", "any", "all", "get",
    "policy", "policies", "company", "employee", "employees", "work", "per", "its", "not",
}


def _tokens(text: str) -> set:
    # Lowercase, split into letters/digits (so "SEV-1" becomes "sev" and "1"), drop words of <=2
    # letters and stopwords, and strip a trailing "s" from longer words (crude plural handling).
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w.rstrip("s") if len(w) > 3 else w for w in words if len(w) > 2 and w not in _STOPWORDS}


# A document must contain at least this fraction of the question's keywords to be returned at all.
MOCK_MIN_COVERAGE = float(os.getenv("MOCK_MIN_COVERAGE", "0.5"))


def _keyword_search(query: str, pool: List[Document], top_k: int) -> List[tuple[Document, float]]:
    """Mock-mode retrieval: rank authorized docs by keyword overlap; abstain below MOCK_MIN_COVERAGE of the question's keywords."""
    q = _tokens(query)
    if not q:
        return []
    scored = []
    for doc in pool:
        title_tokens, content_tokens = _tokens(doc.title), _tokens(doc.content)
        # Gate: what fraction of the question's keywords appear anywhere in this document?
        if len(q & (title_tokens | content_tokens)) / len(q) < MOCK_MIN_COVERAGE:
            continue
        # Rank: matches in the title and in the body both count; the score is capped at 1.0.
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

    # =========================================================================================
    # THE SECURITY-CRITICAL LINE: PRE-RETRIEVAL RBAC.
    # Documents the role may not read are removed from the candidate pool HERE, before any
    # scoring and before anything is sent to the LLM. A restricted document is therefore never
    # retrieved, never put in a prompt, and cannot be leaked by the model no matter how the
    # question is phrased or how well a prompt injection works. (See docs/ADR-001.)
    #
    # The WRONG alternative is POST-filtering: retrieve everything, give it all to the model, and
    # ask it (or filter its output) to hide restricted parts. That puts confidential text inside
    # the prompt, where injection or a model mistake can expose it.
    #
    # +- AWS EXAM [CLF-C02 / DVA-C02] -------------------------------------------------------
    # | Q: Employees in different departments query one shared Bedrock Knowledge Base. How do
    # |    you stop HR documents from reaching engineers?
    # | A: Tag each document with metadata (e.g. allowed_roles / department) and apply a
    # |    METADATA FILTER in the Retrieve call based on the caller's identity (or use separate
    # |    knowledge bases/indexes per audience). Do NOT rely on the prompt to hide data.
    # | WHY: Authorization must be enforced by deterministic code BEFORE the model sees the data.
    # |    This is PRINCIPLE OF LEAST PRIVILEGE: each caller can reach only what their role
    # |    needs. It also illustrates the SHARED RESPONSIBILITY MODEL: AWS secures Bedrock's
    # |    infrastructure and (per AWS) does not use your prompts to train base models, but
    # |    deciding WHO may see WHICH of your documents is entirely the CUSTOMER's job.
    # +---------------------------------------------------------------------------------------
    # =========================================================================================
    authorized_pool = [doc for doc in _vector_store if user_role in doc.allowed_roles]
    logger.info(f"Authorized docs for {user_role}: {len(authorized_pool)} found")

    # Role can read nothing -> abstain immediately (also covers an unknown role).
    if not authorized_pool:
        logger.info(f"No authorized docs found for {user_role}")
        return []

    # Mock mode: keyword ranking over the already-filtered pool (RBAC is identical in both modes).
    if os.getenv("SKIP_INDEXING") == "1":
        result = _keyword_search(query, authorized_pool, top_k)
        logger.info(f"Mock mode: returning {len(result)} documents")
        return result

    # Live mode: embed the QUESTION (one embedding API call per query) and compare it with each
    # authorized document's stored vector.
    query_vec = np.array(get_embedding(query))

    scored_docs = []
    for doc in authorized_pool:
        doc_vec = np.array(doc.embedding)
        # Dot product. Because the embeddings are normalized to length 1 (see Titan's
        # "normalize": True in llm_provider.py), dot product == cosine similarity: 1.0 means
        # "same meaning", near 0 means "unrelated".
        score = float(np.dot(query_vec, doc_vec))
        if score >= SIMILARITY_THRESHOLD:
            scored_docs.append((doc, score))

    # Best matches first, then keep only the top_k (default 3) so the prompt stays small and cheap.
    scored_docs.sort(key=lambda pair: pair[1], reverse=True)
    return scored_docs[:top_k]
