import os
import sys
import json
from pathlib import Path

# Ensure project root is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.retriever import KnowledgeBaseRetriever


def run_retrieval_benchmark():
    # 1. Initialize Retriever
    docs_path = r"c:\Users\Shivam\Desktop\Task\data\docs"
    retriever = KnowledgeBaseRetriever(docs_path)

    # 2. Load Evaluation Questions
    eval_file = r"c:\Users\Shivam\Desktop\Task\data\eval_set.json"
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    questions = eval_data["questions"]

    # Only test questions that actually expect a document source
    # (Unanswerable questions expect no source: expected_sources = [])
    testable_questions = [q for q in questions if len(q.get("expected_sources", [])) > 0]

    total_testable = len(testable_questions)
    hit_at_1 = 0
    hit_at_3 = 0
    failures = []

    print(f"\n==================================================")
    print(f"  RUNNING RETRIEVAL BENCHMARK ({total_testable} Questions)")
    print(f"==================================================\n")

    for q in testable_questions:
        query_id = q["id"]
        query_text = q["question"]
        expected_sources = set(q["expected_sources"])

        # Retrieve top 3 chunks
        retrieved_chunks = retriever.retrieve(query_text, top_k=3)
        retrieved_sources = [doc.metadata.get("source") for doc in retrieved_chunks]

        # Check Hit @ 1
        is_hit_1 = retrieved_sources[0] in expected_sources if retrieved_sources else False
        if is_hit_1:
            hit_at_1 += 1

        # Check Hit @ 3
        is_hit_3 = any(src in expected_sources for src in retrieved_sources)
        if is_hit_3:
            hit_at_3 += 1
        else:
            # Record failure for FAILURES.md
            failures.append({
                "id": query_id,
                "category": q["category"],
                "question": query_text,
                "expected": list(expected_sources),
                "retrieved": retrieved_sources
            })

    # 3. Print Results Summary
    hr_1 = (hit_at_1 / total_testable) * 100
    hr_3 = (hit_at_3 / total_testable) * 100

    print(f"RESULTS:")
    print(f"  Total testable questions: {total_testable}")
    print(f"  Hit Rate @ 1: {hit_at_1}/{total_testable} ({hr_1:.1f}%)")
    print(f"  Hit Rate @ 3: {hit_at_3}/{total_testable} ({hr_3:.1f}%)")
    print(f"  Total Failures: {len(failures)}\n")

    if failures:
        print("--- FAILURE ANALYSIS ---")
        for f in failures:
            print(f"[{f['id']}] Category: {f['category']}")
            print(f"  Q: {f['question']}")
            print(f"  Expected: {f['expected']}")
            print(f"  Retrieved: {f['retrieved']}\n")

    return {
        "hit_at_1_pct": hr_1,
        "hit_at_3_pct": hr_3,
        "failures": failures
    }


if __name__ == "__main__":
    run_retrieval_benchmark()

