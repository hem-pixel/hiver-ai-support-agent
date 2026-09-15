from typing import Dict, Any, Optional
from app.services.classifier import classify_intent
from app.services.retriever import retrieve_historical_resolution
from app.services.reply_generator import generate_draft_reply
from app.services.decision import evaluate_decision


def analyze_customer_message(message: str) -> Dict[str, Any]:
    """Execute the end-to-end 5-stage AI Support Agent pipeline.

    Orchestration:
    Customer Message
            ↓
    Classifier (classify_intent)
            ↓
    Retriever (retrieve_historical_resolution)
            ↓
    Reply Generator (generate_draft_reply)
            ↓
    Decision Engine (evaluate_decision)
            ↓
    Final Pipeline Response

    Returns:
        Dict matching AnalyzeResponse schema.
    """
    clean_message = str(message or "").strip()

    # Handle empty or invalid messages safely
    if not clean_message:
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

    # 1. Intent Classification (Deterministic rule-based)
    classification = classify_intent(clean_message)
    intent = classification["intent"]
    confidence = classification["confidence"]  # None (un-fabricated)

    # 2. Historical Resolution Retrieval (Intent-filtered TF-IDF)
    retrieval = retrieve_historical_resolution(query=clean_message, intent=intent)
    historical_match = retrieval.get("historical_match")

    similarity = retrieval.get("similarity", 0.0)

    # 3. Grounded Draft Reply Generation
    draft_reply = generate_draft_reply(
        intent=intent,
        historical_match=historical_match,
        similarity=similarity
    )

    # 4. Auto-Handle vs Escalate Decision & 5. Decision Reason
    decision_result = evaluate_decision(
        intent=intent,
        similarity=similarity,
        historical_match=historical_match
    )
    decision = decision_result["decision"]
    decision_reason = decision_result["reason"]

    return {
        "message": clean_message,
        "intent": intent,
        "confidence": confidence,
        "historical_match": historical_match,
        "similarity": similarity,
        "draft_reply": draft_reply,
        "decision": decision,
        "decision_reason": decision_reason
    }
