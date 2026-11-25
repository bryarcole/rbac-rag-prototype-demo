"""Precompute document embeddings so app startup makes no embedding API calls.

    set -a; source .env; set +a
    LLM_PROVIDER=gemini python build_embeddings.py

Writes embeddings/<provider>.npz. Commit that file to deploy. Rerun after editing documents or
changing the embedding model; unchanged documents are reused, so an interrupted run can resume.
"""
import os

from documents import SEED_DOCUMENTS
from rag_core import _get_llm, embedding_cache_path, index_documents, save_embedding_cache

# WHY A SEPARATE SCRIPT: embedding is a one-time, paid ingestion step. Doing it here (not on every app
# start) is the same idea as a Bedrock Knowledge Base "ingestion job": documents are converted to
# vectors once, stored, and reused. [AWS EXAM CLF-C02: Cost Optimization pillar - pay for the
# expensive step once.]
#
# Mock mode has no real embeddings, so there is nothing worth saving.
if os.getenv("SKIP_INDEXING") == "1":
    raise SystemExit("Unset SKIP_INDEXING: mock mode has no real embeddings to precompute.")

provider = os.getenv("LLM_PROVIDER", "bedrock").lower()
model = _get_llm().embed_model_name
print(f"Embedding {len(SEED_DOCUMENTS)} documents with {provider} / {model} ...")
# index_documents reuses any vector already in the cache whose text is unchanged, so rerunning this
# after an interruption or a small edit only pays for what is missing or changed.
docs = index_documents(list(SEED_DOCUMENTS))
print(f"Wrote {save_embedding_cache(provider, model, docs)}")
