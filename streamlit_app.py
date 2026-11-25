"""
Streamlit web UI.

HOW STREAMLIT WORKS (the one idea you need to read this file):
    Streamlit re-runs this ENTIRE script, top to bottom, every time the user clicks, types or picks
    something. Nothing "stays" in a normal variable between runs. Values that must survive a re-run
    live in `st.session_state` (a per-browser-session dict). Button `on_click` / `on_change`
    callbacks run FIRST, before the script is re-run, which is how a sample button can change the
    role and question and have the page re-render already showing the answer.
"""
import streamlit as st
from documents import SEED_DOCUMENTS, SCENARIOS, SAMPLE_QUESTIONS
from workflow import run_enterprise_workflow

st.set_page_config(page_title="Permission-Aware Enterprise RAG", page_icon="🛡️", layout="wide")

ROLES = ["employee", "engineering", "hr", "executive"]
# setdefault only sets a value the FIRST time (when the key does not exist yet), so these defaults
# are not overwritten on later re-runs.
st.session_state.setdefault("role", "engineering")
st.session_state.setdefault("question", "")


def use_sample(role: str, question: str):
    # Callback for the sample buttons: switch role and question together, so the click shows the
    # same question answered under the intended role (e.g. HR sees it, employee is blocked).
    st.session_state["role"] = role
    st.session_state["question"] = question


def use_scenario():
    # Callback for the "browse more questions" dropdown: copy the picked question into the box.
    picked = st.session_state["scenario_pick"]
    if picked != "—":
        st.session_state["question"] = picked


with st.sidebar:
    # SECURITY NOTE: this dropdown is a SIMULATED identity for demos. Whoever uses the page can
    # pick any role, which is exactly what real authentication prevents. In production the role
    # would come from a verified login (e.g. Amazon Cognito / IAM Identity Center), never from a
    # control the user can change. [AWS EXAM: authentication = prove who you are; authorization =
    # what you may do. Never authorize from a value the caller supplies.]
    st.header("🔐 Simulated Identity")
    selected_role = st.selectbox("Active User Role", ROLES, key="role")
    st.divider()
    st.subheader("Documents")
    # Split ALL documents into "this role can read" vs "locked". This is DISPLAY ONLY; the real
    # enforcement happens in rag_core.search_authorized_docs, not here.
    authorized = [d for d in SEED_DOCUMENTS if selected_role in d.allowed_roles]
    locked = [d for d in SEED_DOCUMENTS if selected_role not in d.allowed_roles]
    st.caption(f"{len(authorized)} accessible, {len(locked)} locked for `{selected_role}`")
    with st.expander(f"✅ Accessible ({len(authorized)})"):
        for doc in authorized:
            st.markdown(f"**{doc.doc_id}** — {doc.title}")
    # NOTE: this lists the TITLES of documents the role cannot read (e.g. "Project Titan Acquisition
    # Memo (Restricted)"). Useful for a demo, but in a real system the mere existence and title of a
    # restricted document can itself be sensitive, so you would normally hide them.
    with st.expander(f"🔒 Locked ({len(locked)})"):
        for doc in locked:
            st.markdown(f"**{doc.doc_id}** — {doc.title}")

st.title("🛡️ Permission-Aware Enterprise RAG")

st.subheader("Try a sample question")
st.caption("Each button switches to the right role and runs the question. Pairs like “HR sees it / employee blocked” show RBAC in action.")
# dict.fromkeys(...) de-duplicates the category names while KEEPING their original order (a plain
# set() would scramble the tab order).
categories = list(dict.fromkeys(s[0] for s in SAMPLE_QUESTIONS))
for category, tab in zip(categories, st.tabs(categories)):
    with tab:
        items = [s for s in SAMPLE_QUESTIONS if s[0] == category]
        # Each sample is a tuple: (category, label, role, question, _unused). One button per sample.
        for col, (_, label, role, question, _) in zip(st.columns(len(items)), items):
            col.button(
                label,
                key=f"sample_{category}_{label}",
                on_click=use_sample,
                args=(role, question),
                help=f"As {role}: {question}",
                use_container_width=True,
            )

# Each SCENARIO is (question, a role allowed to read the doc, expected doc_id). s[2] is the doc_id.
# Keep only scenarios whose source document the CURRENT role may read, so the dropdown never
# offers a question this role could not get an answer to.
docs_by_id = {d.doc_id: d for d in SEED_DOCUMENTS}
role_scenarios = [s for s in SCENARIOS if selected_role in docs_by_id[s[2]].allowed_roles]
st.selectbox(
    f"Or browse {len(role_scenarios)} more example questions for `{selected_role}`",
    ["—"] + [s[0] for s in role_scenarios],
    key="scenario_pick",
    on_change=use_scenario,
)

question = st.text_input("Ask the enterprise knowledge base:", key="question")

# Runs on EVERY re-run while the box is non-empty, so changing the role re-asks the same question
# as the new role (handy for seeing RBAC change the outcome), and each re-run writes a new audit
# record and, in live mode, makes new paid LLM calls.
if question:
    with st.spinner(f"Running 4-step workflow as `{selected_role}`..."):
        record = run_enterprise_workflow(question=question, user_role=selected_role)

    # Status explains the outcome: answered / blocked_injection / insufficient_context. NOTE that
    # insufficient_context is ALSO what an RBAC denial looks like: the ANSWER never says "a
    # restricted document exists, but you can't see it". So it is not necessarily an error. (The
    # sidebar above does list locked titles; see the note there.)
    st.info(
        f"**Status:** {record.status} | **Triage:** `{record.triage_intent}` | "
        f"**Latency:** {record.latency_ms} ms | **Est. Cost:** ${record.estimated_cost_usd:.6f}"
    )
    st.write(record.answer)
    if record.cited_doc_ids:
        st.caption(f"**Citations:** {', '.join(record.cited_doc_ids)}")
    with st.expander("Inspect Structured Audit Log (JSON)"):
        st.json(record.model_dump())
