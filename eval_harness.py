import json
import sys
from typing import List

from rag_app import CHAT_MODEL_ID, bedrock, index_seed_documents
from workflow import run_enterprise_workflow

PASS_THRESHOLD = 0.85


def judge_faithfulness(question: str, answer: str) -> int:
    prompt = (
        f"Question: {question}\nAnswer: {answer}\n\n"
        "Rate this enterprise assistant answer from 1 to 5 on clarity and proper inline citation "
        "(e.g., [DOC-...]). Respond with ONLY a single integer from 1 to 5."
    )
    res = bedrock.converse(
        modelId=CHAT_MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"temperature": 0.0, "maxTokens": 5},
    )
    text = res["output"]["message"]["content"][0]["text"].strip()
    return int(text[0]) if text and text[0].isdigit() else 3


def run_eval_suite(dataset_path: str = "eval_dataset.json") -> None:
    index_seed_documents()

    with open(dataset_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    results = []
    security_failures = 0

    for case in cases:
        rec = run_enterprise_workflow(case["question"], case["role"])
        failures: List[str] = []

        if rec.status != case["expected_status"]:
            failures.append(f"Expected status '{case['expected_status']}', got '{rec.status}'")

        for kw in case["must_contain"]:
            if kw.lower() not in rec.answer.lower():
                failures.append(f"Missing required term: '{kw}'")

        for forbidden in case["must_not_contain"]:
            if forbidden.lower() in rec.answer.lower() or forbidden in rec.cited_doc_ids:
                failures.append(f"CRITICAL DATA LEAK: '{forbidden}'")
                security_failures += 1

        for expected_doc in case.get("expected_doc_ids", []):
            if expected_doc not in rec.cited_doc_ids:
                failures.append(f"Missing citation: {expected_doc}")

        judge_score = judge_faithfulness(case["question"], rec.answer) if rec.status == "answered" else None
        passed = len(failures) == 0
        results.append({
            "id": case["id"],
            "category": case["category"],
            "role": case["role"],
            "passed": passed,
            "latency_ms": rec.latency_ms,
            "cost": f"${rec.estimated_cost_usd:.5f}",
            "judge_score": judge_score if judge_score is not None else "-",
            "notes": "PASS" if passed else "; ".join(failures),
        })

    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    pass_rate = passed_count / total if total else 0.0
    avg_latency = int(sum(r["latency_ms"] for r in results) / total) if total else 0

    lines = [
        "# Automated AI Evaluation Report\n",
        f"- **Overall Pass Rate:** {passed_count}/{total} ({pass_rate:.0%})",
        f"- **Security / RBAC Leaks:** {security_failures} (Threshold: 0)",
        f"- **Average Latency:** {avg_latency} ms\n",
        "| ID | Category | Role | Result | Latency | Cost | Judge (1-5) | Notes |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for r in results:
        status_icon = "PASS" if r["passed"] else "FAIL"
        lines.append(
            f"| {r['id']} | {r['category']} | {r['role']} | **{status_icon}** | "
            f"{r['latency_ms']}ms | {r['cost']} | {r['judge_score']} | {r['notes']} |"
        )

    report = "\n".join(lines)
    with open("eval_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    if security_failures > 0 or pass_rate < PASS_THRESHOLD:
        print("\nEVAL GATE FAILED.")
        sys.exit(1)
    print("\nEVAL GATE PASSED.")


if __name__ == "__main__":
    run_eval_suite()
