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


SALARY = "What is the base salary band for an L5 Senior Engineer?"
SEV1 = "What are the exact steps for a SEV-1 production outage?"
TITAN = "What is the Project Titan acquisition price?"


@pytest.mark.parametrize(
    "role,question",
    [
        ("employee", SALARY),
        ("engineering", SALARY),
        ("employee", SEV1),
        ("hr", SEV1),
        ("employee", TITAN),
        ("engineering", TITAN),
        ("hr", TITAN),
        ("employee", "What is the capital of France?"),
    ],
)
def test_restricted_or_offtopic_questions_abstain(role, question):
    assert search_authorized_docs(question, role, top_k=3) == []


@pytest.mark.parametrize(
    "role,question,top_doc",
    [
        ("hr", SALARY, "DOC-HR-01"),
        ("executive", SALARY, "DOC-HR-01"),
        ("engineering", SEV1, "DOC-ENG-01"),
        ("executive", TITAN, "DOC-EXEC-01"),
    ],
)
def test_authorized_roles_get_the_right_top_doc(role, question, top_doc):
    hits = search_authorized_docs(question, role, top_k=3)
    assert hits and hits[0][0].doc_id == top_doc


from documents import SAMPLE_QUESTIONS  # noqa: E402
from workflow import run_enterprise_workflow  # noqa: E402


@pytest.mark.parametrize("category,label,role,question,expected", SAMPLE_QUESTIONS)
def test_sample_questions_produce_expected_status(category, label, role, question, expected):
    assert role in ROLES
    assert run_enterprise_workflow(question=question, user_role=role).status == expected
