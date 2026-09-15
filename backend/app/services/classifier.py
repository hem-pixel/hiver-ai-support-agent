from typing import Dict, List, Any, Optional

# Standard 10-intent taxonomy for customer support
INTENT_TAXONOMY: List[str] = [
    "fare_or_charge_issue",
    "refund_request",
    "driver_issue",
    "trip_issue",
    "cancellation_issue",
    "account_access_issue",
    "payment_issue",
    "app_or_technical_issue",
    "uber_eats_issue",
    "other_support_issue"
]

INTENT_KEYWORDS: Dict[str, List[str]] = {
    "uber_eats_issue": [
        "uber eats", "eats", "food", "restaurant", "delivery",
        "order", "meal", "menu", "driver delivering"
    ],
    "account_access_issue": [
        "account", "login", "log in", "logged in", "password",
        "deactivated", "locked", "sign in", "phone number", "email"
    ],
    "driver_issue": [
        "driver", "pickup", "pick up", "rude", "behavior",
        "didn't show", "did not show", "speeding", "seat belt"
    ],
    "cancellation_issue": [
        "cancel", "cancelled", "canceled", "cancellation"
    ],
    "refund_request": [
        "refund", "money back", "reimburse", "reimbursement"
    ],
    "fare_or_charge_issue": [
        "fare", "charged", "charge", "overcharged",
        "expensive", "price", "surge"
    ],
    "payment_issue": [
        "payment", "card", "cash", "credit card",
        "debit card", "billing", "transaction", "pay"
    ],
    "app_or_technical_issue": [
        "app", "error", "crash", "technical",
        "bug", "not working", "link", "website"
    ],
    "trip_issue": [
        "trip", "ride", "journey", "route",
        "destination", "drop off", "dropoff"
    ]
}


def classify_intent(text: str) -> Dict[str, Any]:
    """Classify customer message into one of 10 support intents.

    Uses deterministic rule-based keyword matching aligned with baseline_rules.py.
    Returns:
        {
            "intent": str,
            "confidence": None  # Preserved as None (never fabricated)
        }
    """
    clean_text = str(text or "").lower().strip()
    if not clean_text:
        return {
            "intent": "other_support_issue",
            "confidence": None
        }

    scores: Dict[str, int] = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in clean_text)
        scores[intent] = score

    best_intent = max(scores, key=scores.get)

    # Fallback to other_support_issue if no keyword hits
    if scores[best_intent] == 0:
        return {
            "intent": "other_support_issue",
            "confidence": None
        }

    return {
        "intent": best_intent,
        "confidence": None
    }
