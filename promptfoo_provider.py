"""
Custom Promptfoo Python provider that routes prompts through our full 4-step RBAC RAG workflow
and allows A/B testing across any Amazon Bedrock Converse-compatible model ID.
"""
from rag_app import VECTOR_STORE, index_seed_documents
from workflow import run_enterprise_workflow


def call_api(prompt: str, options: dict, context: dict) -> dict:
    if not VECTOR_STORE:
        index_seed_documents()

    config = options.get("config", {})
    model_id = config.get("model_id", "us.amazon.nova-2-lite-v1:0")
    vars_dict = context.get("vars", {})
    user_role = vars_dict.get("role", "employee")

    rec = run_enterprise_workflow(question=prompt, user_role=user_role, model_id=model_id)

    return {
        "output": rec.answer,
        "tokenUsage": {
            "prompt": rec.input_tokens,
            "completion": rec.output_tokens,
            "total": rec.input_tokens + rec.output_tokens,
        },
        "cost": rec.estimated_cost_usd,
        "metadata": {
            "status": rec.status,
            "triage_intent": rec.triage_intent,
            "cited_doc_ids": rec.cited_doc_ids,
            "latency_ms": rec.latency_ms,
        },
    }
