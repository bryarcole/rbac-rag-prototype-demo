import streamlit as st
from documents import SEED_DOCUMENTS, SCENARIOS, SAMPLE_QUESTIONS
from workflow import run_enterprise_workflow

st.set_page_config(page_title="Permission-Aware Enterprise RAG", page_icon="🛡️", layout="wide")

ROLES = ["employee", "engineering", "hr", "executive"]
st.session_state.setdefault("role", "engineering")
st.session_state.setdefault("question", "")


def use_sample(role: str, question: str):
    st.session_state["role"] = role
    st.session_state["question"] = question


def use_scenario():
    picked = st.session_state["scenario_pick"]
    if picked != "—":
        st.session_state["question"] = picked


with st.sidebar:
    st.header("🔐 Simulated Identity")
    selected_role = st.selectbox("Active User Role", ROLES, key="role")
    st.divider()
    st.subheader("Documents")
    authorized = [d for d in SEED_DOCUMENTS if selected_role in d.allowed_roles]
    locked = [d for d in SEED_DOCUMENTS if selected_role not in d.allowed_roles]
    st.caption(f"{len(authorized)} accessible, {len(locked)} locked for `{selected_role}`")
    with st.expander(f"✅ Accessible ({len(authorized)})"):
        for doc in authorized:
            st.markdown(f"**{doc.doc_id}** — {doc.title}")
    with st.expander(f"🔒 Locked ({len(locked)})"):
        for doc in locked:
            st.markdown(f"**{doc.doc_id}** — {doc.title}")

st.title("🛡️ Permission-Aware Enterprise RAG")

st.subheader("Try a sample question")
st.caption("Each button switches to the right role and runs the question. Pairs like “HR sees it / employee blocked” show RBAC in action.")
categories = list(dict.fromkeys(s[0] for s in SAMPLE_QUESTIONS))
for category, tab in zip(categories, st.tabs(categories)):
    with tab:
        items = [s for s in SAMPLE_QUESTIONS if s[0] == category]
        for col, (_, label, role, question, _) in zip(st.columns(len(items)), items):
            col.button(
                label,
                key=f"sample_{category}_{label}",
                on_click=use_sample,
                args=(role, question),
                help=f"As {role}: {question}",
                use_container_width=True,
            )

docs_by_id = {d.doc_id: d for d in SEED_DOCUMENTS}
role_scenarios = [s for s in SCENARIOS if selected_role in docs_by_id[s[2]].allowed_roles]
st.selectbox(
    f"Or browse {len(role_scenarios)} more example questions for `{selected_role}`",
    ["—"] + [s[0] for s in role_scenarios],
    key="scenario_pick",
    on_change=use_scenario,
)

question = st.text_input("Ask the enterprise knowledge base:", key="question")

if question:
    with st.spinner(f"Running 4-step workflow as `{selected_role}`..."):
        record = run_enterprise_workflow(question=question, user_role=selected_role)

    st.info(
        f"**Status:** {record.status} | **Triage:** `{record.triage_intent}` | "
        f"**Latency:** {record.latency_ms} ms | **Est. Cost:** ${record.estimated_cost_usd:.6f}"
    )
    st.write(record.answer)
    if record.cited_doc_ids:
        st.caption(f"**Citations:** {', '.join(record.cited_doc_ids)}")
    with st.expander("Inspect Structured Audit Log (JSON)"):
        st.json(record.model_dump())
