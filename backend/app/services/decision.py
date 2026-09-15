from typing import Dict, Any, Optional

# Preserved baseline similarity threshold from evaluation/agent.py
DEFAULT_SIMILARITY_THRESHOLD = 0.20

ESCALATION_PHRASES = [
    "send us a dm",
    "send us a note",
    "contact us",
    "direct messages",
    "send us a message",
    "dm us",
    "follow up via dm",
    "reach out via dm",
    "get in touch"
]


def evaluate_decision(
    intent: str,
    similarity: float,
    historical_match: Optional[Dict[str, str]],
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
) -> Dict[str, str]:
    """Determine whether an inquiry should be AUTO_HANDLE or ESCALATE.

    Decision Policy:
    AUTO_HANDLE only when:
    - predicted intent is deterministic/clear
    - usable historical resolution exists
    - similarity >= 0.20
    - historical response provides self-contained guidance
    - no direct human intervention is required

    ESCALATE when:
    - similarity < 0.20
    - no usable historical resolution exists
    - historical response requests DM/direct support
    - issue requires identity verification/account action
    - issue is ambiguous or requires an action the system cannot perform
    """
    # 1. Similarity below threshold or no usable historical resolution exists
    if not historical_match or similarity < similarity_threshold:
        return {
            "decision": "ESCALATE",
            "reason": (
                f"No usable historical resolution found (similarity {similarity:.4f} "
                f"is below {similarity_threshold:.2f} threshold)."
            )
        }

    # 2. Ambiguous intent: other_support_issue is non-deterministic fallback
    if intent == "other_support_issue":
        return {
            "decision": "ESCALATE",
            "reason": "Inquiry intent is ambiguous or unclassified; requires human agent triage."
        }

    # 3. Action system cannot perform: financial refund processing
    if intent == "refund_request":
        return {
            "decision": "ESCALATE",
            "reason": "Refund requests require transaction verification and authorized financial processing."
        }

    # 4. Issue requires identity verification or account-level action
    if intent == "account_access_issue":
        return {
            "decision": "ESCALATE",
            "reason": "Account access inquiries require secure identity verification and human support intervention."
        }

    raw_response = historical_match.get("support_response", "")
    response_lower = raw_response.lower()

    # 5. Historical response requests DM / direct support / manual review
    if any(phrase in response_lower for phrase in ESCALATION_PHRASES):
        return {
            "decision": "ESCALATE",
            "reason": "Historical responses indicate that this issue requires direct support follow-up."
        }

    # 6. Clear deterministic intent with self-contained resolution guidance
    return {
        "decision": "AUTO_HANDLE",
        "reason": f"A usable historical resolution was found (similarity: {similarity:.4f}) with self-contained guidance."
    }

