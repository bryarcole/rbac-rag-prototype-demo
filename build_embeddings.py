"""Precompute document embeddings so app startup makes no embedding API calls.

    set -a; source .env; set +a
    LLM_PROVIDER=gemini python build_embeddings.py

Writes embeddings/<provider>.npz. Commit that file to deploy. Rerun after editing documents or
changing the embedding model; unchanged documents are reused, so an interrupted run can resume.
"""
import os

from documents import SEED_DOCUMENTS
from rag_core import _get_llm, embedding_cache_path, index_documents, save_embedding_cache

if os.getenv("SKIP_INDEXING") == "1":
    raise SystemExit("Unset SKIP_INDEXING: mock mode has no real embeddings to precompute.")

provider = os.getenv("LLM_PROVIDER", "bedrock").lower()
model = _get_llm().embed_model_name
print(f"Embedding {len(SEED_DOCUMENTS)} documents with {provider} / {model} ...")
docs = index_documents(list(SEED_DOCUMENTS))
print(f"Wrote {save_embedding_cache(provider, model, docs)}")
