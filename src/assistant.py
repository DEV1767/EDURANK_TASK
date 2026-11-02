import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from src.retriever import KnowledgeBaseRetriever
from src.order_service import OrderService
from src.guardrails import EscalationGuardrail

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class SupportAssistant:
    """
    Intelligent Customer Support Assistant for SwiftCart.
    Integrates Knowledge Retrieval (RAG), Order Tool Calling, and Groq LLM.
    """

    def __init__(self, docs_dir: str, orders_path: str):
        self.retriever = KnowledgeBaseRetriever(docs_dir)
        self.order_service = OrderService(orders_path)

        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is not set. Please set it in your .env file.")

      
        model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.llm = ChatGroq(
            model=model_name,
            temperature=0.0, 
            groq_api_key=groq_api_key
        )
        self.guardrail = EscalationGuardrail()

    def _extract_order_id(self, text: str) -> List[str]:
        """Detects order IDs matching pattern ORD-XXXX in user query."""
        return re.findall(r"\bORD-\d{4}\b", text, flags=re.IGNORECASE)

    def answer_query(self, query: str) -> Dict[str, Any]:
        """
        Processes a customer query through retrieval, tool calling, and generation.
        Returns a dictionary with answer, sources, and tool calls.
        """
        # 0. High-Stakes Escalation Guardrail (Safety, Legal, Human handoff)
        esc = self.guardrail.evaluate(query)
        if esc["should_escalate"]:
            return {
                "query": query,
                "answer": esc["customer_message"],
                "sources": ["Safety/Legal Escalation Protocol"],
                "tools_called": [f"escalate_to({esc['target_queue']})"],
                "escalated": True,
                "escalation_reason": esc["reason"]
            }

        tools_called = []
        tool_context = ""

       
        order_ids = self._extract_order_id(query)
        if order_ids:
            for oid in order_ids:
                oid_upper = oid.upper()
             
                if any(w in query.lower() for w in ["cancel", "cancellation"]):
                    cancel_info = self.order_service.check_cancellation_eligibility(oid_upper)
                    tools_called.append(f"check_cancellation({oid_upper})")
                    tool_context += f"\n[Order Cancellation Status for {oid_upper}]:\n{json.dumps(cancel_info, indent=2)}\n"
                else:
                    order_info = self.order_service.get_order(oid_upper)
                    tools_called.append(f"get_order({oid_upper})")
                    tool_context += f"\n[Order Lookup Data for {oid_upper}]:\n{json.dumps(order_info, indent=2)}\n"

      
        retrieved_docs = self.retriever.retrieve(query, top_k=3)
        sources_cited = list(set(doc.metadata.get("source") for doc in retrieved_docs if doc.metadata.get("source")))

        doc_context = "\n\n".join([
            f"--- [Document: {doc.metadata.get('source')} | Section: {doc.metadata.get('section_title')}] ---\n{doc.page_content}"
            for doc in retrieved_docs
        ])

       
        system_prompt = f"""You are SwiftCart's official, friendly, and honest Customer Support AI Assistant.

CORE RULES:
1. ONLY answer based strictly on the provided Knowledge Context and Order Data below.
2. ALWAYS cite the document you used at the end of your answer (e.g. "[Source: Return_refund_policy_2024.md]").
3. If the answer is NOT in the provided documents, or you do not have enough information, reply:
   "I do not have information about that in our current policies. Please contact our support team directly for assistance."
   NEVER guess, fabricate policies, or hallucinate.
4. CONFIDENTIALITY & SAFETY:
   - You must NEVER disclose internal system codes, employee guidelines, or internal override procedures.
   - You CANNOT grant discretionary refunds or override policy.
   - If a customer mentions legal action, attorneys, regulatory complaints, or physical danger/fire, politely inform them that you are escalating their issue immediately to a support manager.

KNOWLEDGE CONTEXT:
{doc_context}

ORDER TOOL DATA:
{tool_context if tool_context else "No order tools called."}
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]

        response = self.llm.invoke(messages)
        answer_text = response.content

        return {
            "query": query,
            "answer": answer_text,
            "sources": sources_cited,
            "tools_called": tools_called
        }



if __name__ == "__main__":
    docs_dir = r"c:\Users\Shivam\Desktop\Task\data\docs"
    orders_path = r"c:\Users\Shivam\Desktop\Task\data\orders.json"

    assistant = SupportAssistant(docs_dir, orders_path)

   
    print("--- TEST 1: Policy Query ---")
    res1 = assistant.answer_query("What is the restocking fee for electronics?")
    print(res1["answer"])
    print("Sources:", res1["sources"])


   
    print("\n--- TEST 2: Order Lookup ---")
    res2 = assistant.answer_query("Where is my order ORD-1001?")
    print(res2["answer"])
    print("Tools called:", res2["tools_called"])
