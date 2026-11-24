import os

import pytest

os.environ["SKIP_INDEXING"] = "1"

from documents import SCENARIOS, SEED_DOCUMENTS  # noqa: E402
from rag_core import search_authorized_docs  # noqa: E402

DOCS_BY_ID = {d.doc_id: d for d in SEED_DOCUMENTS}
ROLES = {"employee", "engineering", "hr", "executive"}


def test_doc_ids_unique():
    ids = [d.doc_id for d in SEED_DOCUMENTS]
    assert len(ids) == len(set(ids))


def test_roles_valid_and_scenarios_authorized():
    for d in SEED_DOCUMENTS:
        assert d.allowed_roles and set(d.allowed_roles) <= ROLES, d.doc_id
    for question, role, doc_id in SCENARIOS:
        assert role in DOCS_BY_ID[doc_id].allowed_roles, (question, role, doc_id)


@pytest.mark.parametrize("question,role,doc_id", SCENARIOS)
def test_scenario_retrieves_expected_doc(question, role, doc_id):
    hits = [d.doc_id for d, _ in search_authorized_docs(question, role, top_k=5)]
    assert doc_id in hits, f"{doc_id} not in top-5 {hits}"


@pytest.mark.parametrize("question,role,doc_id", SCENARIOS)
def test_unauthorized_roles_never_see_doc(question, role, doc_id):
    for other in ROLES - set(DOCS_BY_ID[doc_id].allowed_roles):
        hits = [d.doc_id for d, _ in search_authorized_docs(question, other, top_k=10)]
        assert doc_id not in hits
