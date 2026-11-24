from pathlib import Path

import numpy as np
import pytest

import rag_core
from documents import SEED_DOCUMENTS

CACHE_FILES = sorted(Path(rag_core.EMBEDDINGS_DIR).glob("*.npz"))


class _FakeLLM:
    embed_model_name = "fake-embed-v1"


@pytest.fixture
def live_mode(monkeypatch, tmp_path):
    """Non-mock indexing with a fake provider and an empty cache directory; records embedding API calls."""
    monkeypatch.delenv("SKIP_INDEXING", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setattr(rag_core, "EMBEDDINGS_DIR", tmp_path)
    monkeypatch.setattr(rag_core, "_get_llm", lambda: _FakeLLM())
    calls = []
    monkeypatch.setattr(rag_core, "get_embedding", lambda text: calls.append(text) or [0.5, 0.5])
    return calls


@pytest.mark.parametrize("path", CACHE_FILES, ids=lambda p: p.name)
def test_committed_cache_matches_current_documents(path):
    """A stale cache would silently serve embeddings for old document text. Rebuild with build_embeddings.py."""
    with np.load(path) as data:
        cached = dict(zip(map(str, data["ids"]), map(str, data["hashes"])))
        assert data["vectors"].shape[0] == len(cached)
    current = {d.doc_id: rag_core._text_hash(rag_core._doc_text(d)) for d in SEED_DOCUMENTS}
    assert cached == current, f"{path.name} is out of date; rerun build_embeddings.py"


def test_cache_roundtrip_skips_embedding_calls(live_mode):
    docs = [d.model_copy(deep=True) for d in SEED_DOCUMENTS[:3]]
    for d in docs:
        d.embedding = [0.1, 0.2]
    rag_core.save_embedding_cache("fake", "fake-embed-v1", docs)

    fresh = [d.model_copy(deep=True, update={"embedding": None}) for d in SEED_DOCUMENTS[:3]]
    rag_core.index_documents(fresh)

    assert live_mode == []
    assert all(d.embedding == pytest.approx([0.1, 0.2]) for d in fresh)


def test_changed_document_is_reembedded_alone(live_mode):
    docs = [d.model_copy(deep=True) for d in SEED_DOCUMENTS[:3]]
    for d in docs:
        d.embedding = [0.1, 0.2]
    rag_core.save_embedding_cache("fake", "fake-embed-v1", docs)

    fresh = [d.model_copy(deep=True, update={"embedding": None}) for d in SEED_DOCUMENTS[:3]]
    fresh[1].content += " edited"
    rag_core.index_documents(fresh)

    assert len(live_mode) == 1 and "edited" in live_mode[0]
    assert fresh[1].embedding == [0.5, 0.5]


def test_cache_built_with_other_model_is_ignored(live_mode):
    docs = [d.model_copy(deep=True) for d in SEED_DOCUMENTS[:2]]
    for d in docs:
        d.embedding = [0.1, 0.2]
    rag_core.save_embedding_cache("fake", "some-other-model", docs)

    fresh = [d.model_copy(deep=True, update={"embedding": None}) for d in SEED_DOCUMENTS[:2]]
    rag_core.index_documents(fresh)

    assert len(live_mode) == 2
