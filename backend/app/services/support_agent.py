import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure repository root and evaluation directory are in sys.path
REPO_ROOT = Path(__file__).resolve().parents[3]
EVAL_DIR = REPO_ROOT / "evaluation"

for path_str in [str(REPO_ROOT), str(EVAL_DIR)]:
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

# Reuse existing retriever and agent evaluation logic
import retriever
import agent


def analyze_customer_message(message: str) -> Dict[str, Any]:
    """Execute the 5-stage AI support-agent pipeline on a customer inquiry.

    Reuses existing logic from evaluation/retriever.py and evaluation/agent.py:
    1. Intent classification (keyword rule-based baseline)
    2. Intent-filtered historical resolution retrieval (TF-IDF cosine similarity)
    3. Grounded draft reply generation
    4. Auto-handle vs escalate decision
    5. Decision rationale

    Returns:
        Dict containing message, intent, confidence, historical_match,
        similarity, draft_reply, decision, and decision_reason.
    """
    cleaned_message = (message or "").strip()
    if not cleaned_message:
        return {
            "message": message,
            "intent": "other_support_issue",
            "confidence": None,
            "historical_match": None,
            "similarity": 0.0,
            "draft_reply": (
                "Sorry you're experiencing this issue. "
                "Please contact our support team with your details so we can assist you."
            ),
            "decision": "ESCALATE",
            "decision_reason": "Customer message was empty or invalid."
        }

    # 1. Intent Classification
    intent = retriever.classify_intent(cleaned_message)

    # 2. Historical Resolution Retrieval
    historical_match: Optional[Dict[str, str]] = None
    similarity: float = 0.0
    draft: str = ""
    decision: str = "ESCALATE"
    reason: str = ""

    try:
        results = retriever.retrieve(cleaned_message, top_k=1)
        if results and len(results) > 0:
            best = results[0]
            similarity = float(best.get("similarity", 0.0))
            historical_customer = str(best.get("customer_message", ""))
            historical_response = str(best.get("support_response", ""))

            historical_match = {
                "customer_message": historical_customer,
                "support_response": historical_response
            }

            # 3. Draft Reply Generation
            draft = agent.draft_reply(intent, historical_response)

            # 4. Auto-handle vs Escalate Decision & 5. Decision Reason
            decision, reason = agent.decide_action(intent, similarity, historical_response)
        else:
            draft = agent.draft_reply(intent, "")
            decision = "ESCALATE"
            reason = "No historical resolution match was found in the resolution corpus."

    except Exception as exc:
        # Fallback gracefully in case of retrieval or parsing errors
        draft = agent.draft_reply(intent, "")
        decision = "ESCALATE"
        reason = f"Retrieval encountered an unexpected issue: {str(exc)}"

    # Note on confidence: The rule-based classifier does not compute calibrated
    # probabilities, so confidence is strictly returned as None (null) without fabrication.
    return {
        "message": cleaned_message,
        "intent": intent,
        "confidence": None,
        "historical_match": historical_match,
        "similarity": similarity,
        "draft_reply": draft,
        "decision": decision,
        "decision_reason": reason
    }
