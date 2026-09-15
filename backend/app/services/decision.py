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
    """Determine whether an inquiry should be AUTO_HANDLE or ESCALATE with justification.

    ESCALATE when:
    - No historical match exists
    - Similarity < 0.20 threshold
    - Historical response indicates direct human support follow-up (DM, note, manual review)
    - Sensitive account security issues require human verification

    AUTO_HANDLE when:
    - Sufficiently similar historical resolution exists (>= 0.20)
    - Historical resolution is self-contained guidance without requiring direct human follow-up
    """
    # 1. No historical match found
    if not historical_match:
        return {
            "decision": "ESCALATE",
            "reason": "No suitable historical resolution match was found in the resolution corpus."
        }

    # 2. Similarity below threshold
    if similarity < similarity_threshold:
        return {
            "decision": "ESCALATE",
            "reason": f"No sufficiently similar historical resolution was found (similarity {similarity:.4f} is below {similarity_threshold:.2f} threshold)."
        }

    raw_response = historical_match.get("support_response", "")
    response_lower = raw_response.lower()

    # 3. Historical response indicates direct human follow-up
    if any(phrase in response_lower for phrase in ESCALATION_PHRASES):
        return {
            "decision": "ESCALATE",
            "reason": "Historical responses indicate that this issue requires direct support follow-up."
        }

    # 4. Sensitive issues requiring manual authentication
    if intent == "account_access_issue" and "deactivated" in historical_match.get("customer_message", "").lower():
        return {
            "decision": "ESCALATE",
            "reason": "Account access and deactivation inquiries require human agent identity verification."
        }

    # 5. Clear resolution ready for auto-handle
    return {
        "decision": "AUTO_HANDLE",
        "reason": f"A sufficiently similar historical resolution was found (similarity: {similarity:.4f}) with self-serve guidance."
    }
