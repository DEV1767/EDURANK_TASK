import os
import sys
import json
import re
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.assistant import SupportAssistant


def evaluate_response(q_item: dict, response: dict) -> dict:
    """
    Evaluates whether the assistant's answer is correct based on:
    1. Action alignment (answer vs refuse vs escalate)
    2. Criteria satisfaction (presence of key required facts/actions)
    """
    expected_action = q_item.get("expected_action", "answer")
    answer = response["answer"].strip()
    lower_answer = answer.lower()

    # 1. Check Safe Refusal
    if expected_action == "refuse":
        refusal_phrases = ["do not have information", "not have information", "cannot", "please contact", "not available", "unable to", "can't"]
        is_refusal = any(phrase in lower_answer for phrase in refusal_phrases)
        is_correct = is_refusal
        return {
            "is_correct": is_correct,
            "reason": "Correctly refused unanswerable/restricted query." if is_correct else "Failed to refuse appropriately."
        }

    # 2. Check Human Escalation
    if expected_action == "escalate_human":
        escalation_phrases = ["escalat", "manager", "support team", "supervisor"]
        is_escalation = any(phrase in lower_answer for phrase in escalation_phrases)
        return {
            "is_correct": is_escalation,
            "reason": "Triggered human escalation as required." if is_escalation else "Failed to escalate high-stakes issue."
        }

    # 3. Check Standard Answer
    expected_ans = q_item["expected_answer"]
    criteria = q_item.get("evaluation_criteria", "")
    key_terms = []
    if "$5" in expected_ans: key_terms.append("$5")
    if "30 days" in expected_ans: key_terms.append("30")
    if "48 hours" in expected_ans: key_terms.append("48")
    if "1-year" in expected_ans or "1 year" in expected_ans: key_terms.append("1")
    if "Canada" in expected_ans: key_terms.append("canada")
    if "United Kingdom" in expected_ans or "UK" in expected_ans: key_terms.append("uk")

    has_key_facts = all(term.lower() in lower_answer for term in key_terms)
    did_not_falsely_refuse = "do not have information" not in lower_answer or "5-7" in lower_answer

    is_correct = has_key_facts and did_not_falsely_refuse
    return {
        "is_correct": is_correct,
        "reason": "Accurately answered with key facts." if is_correct else f"Missed key facts matching criteria: {criteria}"
    }


def run_full_evaluation():
    docs_dir = r"c:\Users\Shivam\Desktop\Task\data\docs"
    orders_path = r"c:\Users\Shivam\Desktop\Task\data\orders.json"
    eval_file = r"c:\Users\Shivam\Desktop\Task\data\eval_set.json"

    print("Initializing SupportAssistant for evaluation run...")
    assistant = SupportAssistant(docs_dir, orders_path)

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    questions = eval_data["questions"]
    total = len(questions)
    passed = 0
    category_scores = {}
    failures = []

    print(f"\n=======================================================")
    print(f"  RUNNING FULL 40-QUESTION EVALUATION BENCHMARK")
    print(f"=======================================================\n")

    for i, q in enumerate(questions, 1):
        cat = q["category"]
        if cat not in category_scores:
            category_scores[cat] = {"passed": 0, "total": 0}
        category_scores[cat]["total"] += 1

        response = assistant.answer_query(q["question"])
        eval_result = evaluate_response(q, response)

        if eval_result["is_correct"]:
            passed += 1
            category_scores[cat]["passed"] += 1
            status = "PASS"
        else:
            status = "FAIL"
            failures.append({
                "id": q["id"],
                "category": cat,
                "question": q["question"],
                "reason": eval_result["reason"],
                "answer_preview": response["answer"][:160]
            })

        print(f"[{q['id']}] ({status}) [{cat}] Q: {q['question'][:50]}...")

    score_pct = (passed / total) * 100
    print(f"\n=======================================================")
    print(f"  EVALUATION RESULTS: {passed}/{total} ({score_pct:.1f}%)")
    print(f"=======================================================\n")

    print("CATEGORY BREAKDOWN:")
    for cat, stat in category_scores.items():
        pct = (stat["passed"] / stat["total"]) * 100 if stat["total"] else 0
        print(f" - {cat:30}: {stat['passed']}/{stat['total']} ({pct:.1f}%)")

    if failures:
        print(f"\nFAILURES REQUIRING ATTENTION ({len(failures)}):")
        for f in failures:
            print(f" - [{f['id']}] {f['question']}")
            print(f"   Reason: {f['reason']}")
            print(f"   Response: {f['answer_preview']}...\n")

    return {
        "passed": passed,
        "total": total,
        "score_pct": score_pct,
        "category_scores": category_scores,
        "failures": failures
    }


if __name__ == "__main__":
    run_full_evaluation()

