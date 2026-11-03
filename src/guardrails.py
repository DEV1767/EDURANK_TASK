import re
from typing import Dict, Any, Optional


class EscalationGuardrail:
    """
    Evaluates customer messages for high-stakes triggers requiring immediate
    human intervention, bypassing automated policy responses.
    """

   
    SAFETY_PATTERNS = [
        r"\b(fire|caught fire|sparking|spark|exploded|explosion|overheated|battery swelling|smoke|burned|shocked|electric shock|injury|hospital)\b"
    ]

   
    LEGAL_PATTERNS = [
        r"\b(attorney|lawyer|legal action|lawsuit|sue|suing|ftc|bbb|better business bureau|attorney general|regulatory complaint|consumer protection)\b"
    ]

   
    HUMAN_REQUEST_PATTERNS = [
        r"\b(speak to a human|talk to a person|real person|human agent|manager|supervisor|get me someone else)\b",
        r"\b(scam|fraud|stolen money|chargeback|unauthorized charge)\b"
    ]

    def evaluate(self, query: str) -> Dict[str, Any]:
        """
        Scans a customer message for escalation triggers.
        Returns a dictionary with routing decision, queue, and customer response.
        """
        clean_text = query.lower()

       
        for pattern in self.SAFETY_PATTERNS:
            if re.search(pattern, clean_text):
                return {
                    "should_escalate": True,
                    "priority": "CRITICAL",
                    "reason": "Physical safety hazard reported (fire, injury, or electrical hazard).",
                    "target_queue": "#support-safety",
                    "customer_message": (
                        "Please ensure your immediate physical safety first. I have flagged this as an urgent, "
                        "high-priority safety incident. A member of our safety response team has been notified "
                        "and will reach out to you immediately."
                    )
                }

       
        for pattern in self.LEGAL_PATTERNS:
            if re.search(pattern, clean_text):
                return {
                    "should_escalate": True,
                    "priority": "HIGH",
                    "reason": "Legal action or regulatory complaint mentioned.",
                    "target_queue": "#legal-escalate",
                    "customer_message": (
                        "I understand the seriousness of your concern. Because this matter involves potential legal "
                        "or regulatory considerations, I am escalating this conversation directly to our senior support "
                        "management team for review."
                    )
                }

       
        for pattern in self.HUMAN_REQUEST_PATTERNS:
            if re.search(pattern, clean_text):
                return {
                    "should_escalate": True,
                    "priority": "MEDIUM",
                    "reason": "Customer requested human supervisor or reported fraudulent activity.",
                    "target_queue": "#tier2-support",
                    "customer_message": (
                        "I understand you would like to speak directly with a team member. I am connecting you with a "
                        "live support representative now who will take over this conversation."
                    )
                }

       
        return {
            "should_escalate": False,
            "priority": "NONE",
            "reason": "Standard query suitable for automated handling.",
            "target_queue": None,
            "customer_message": None
        }


if __name__ == "__main__":
    guard = EscalationGuardrail()

    test_cases = [
        "What is the return window for clothing?",
        "The battery started smoking and burned my nightstand!",
        "I demand my money back or my lawyer will file an FTC complaint!",
        "Can I speak with a real person right now? This is frustrating.",
    ]

    print("=== TESTING ESCALATION GUARDRAIL ===")
    for text in test_cases:
        res = guard.evaluate(text)
        print(f"\nQuery: \"{text}\"")
        print(f"  Escalate: {res['should_escalate']} | Priority: {res['priority']} | Queue: {res['target_queue']}")
        if res["should_escalate"]:
            print(f"  Response: {res['customer_message'][:100]}...")

