import os
import sys
import argparse
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.assistant import SupportAssistant


def format_response(res: dict):
    print("\n" + "=" * 60)
    print(" SWIFTCART ASSISTANT RESPONSE")
    print("=" * 60)
    print(res["answer"])
    print("-" * 60)
    
    if res.get("tools_called"):
        print(f"Tools Called: {', '.join(res['tools_called'])}")
    if res.get("sources"):
        print(f" Sources Cited: {', '.join(res['sources'])}")
    if res.get("escalated"):
        print(f"  ESCALATED: {res.get('escalation_reason')}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="SwiftCart AI Support Assistant CLI")
    parser.add_argument("--query", "-q", type=str, help="Single query to ask the assistant")
    parser.add_argument("--docs", type=str, default="data/docs", help="Path to markdown docs directory")
    parser.add_argument("--orders", type=str, default="data/orders.json", help="Path to orders.json")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    docs_path = project_root / args.docs
    orders_path = project_root / args.orders

    if not docs_path.exists():
        print(f"Error: Documentation directory not found at {docs_path}")
        sys.exit(1)
    if not orders_path.exists():
        print(f"Error: Orders database not found at {orders_path}")
        sys.exit(1)

    print("Loading SwiftCart Assistant...")
    assistant = SupportAssistant(str(docs_path), str(orders_path))
    print("Ready!\n")

    
    if args.query:
        if not args.query.strip():
            print("Error: Query cannot be empty.")
            sys.exit(1)
        res = assistant.answer_query(args.query)
        format_response(res)
        return

   
    print("=== SwiftCart Interactive Support CLI ===")
    print("Type your question below. Type 'exit' or 'quit' to end.\n")

    while True:
        try:
            user_input = input("Customer > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break

            res = assistant.answer_query(user_input)
            format_response(res)

        except (KeyboardInterrupt, EOFError):
            print("\nSession ended. Goodbye!")
            break


if __name__ == "__main__":
    main()
