from typing import Dict, List, Optional
from app.models import Intent


class IntentClassifier:
    """Keyword rule-based intent classifier for customer support messages.

    Covers 10 intents from the Uber Customer Support taxonomy.
    """

    INTENT_KEYWORDS: Dict[str, List[str]] = {
        Intent.UBER_EATS_ISSUE.value: [
            "uber eats", "eats", "food", "restaurant", "delivery",
            "order", "meal", "menu", "driver delivering"
        ],
        Intent.ACCOUNT_ACCESS_ISSUE.value: [
            "account", "login", "log in", "logged in", "password",
            "deactivated", "locked", "sign in", "phone number", "email"
        ],
        Intent.DRIVER_ISSUE.value: [
            "driver", "pickup", "pick up", "rude", "behavior",
            "didn't show", "did not show", "speeding", "seat belt"
        ],
        Intent.CANCELLATION_ISSUE.value: [
            "cancel", "cancelled", "canceled", "cancellation"
        ],
        Intent.REFUND_REQUEST.value: [
            "refund", "money back", "reimburse", "reimbursement"
        ],
        Intent.FARE_OR_CHARGE_ISSUE.value: [
            "fare", "charged", "charge", "overcharged",
            "expensive", "price", "surge"
        ],
        Intent.PAYMENT_ISSUE.value: [
            "payment", "card", "cash", "credit card",
            "debit card", "billing", "transaction", "pay"
        ],
        Intent.APP_OR_TECHNICAL_ISSUE.value: [
            "app", "error", "crash", "technical",
            "bug", "not working", "link", "website"
        ],
        Intent.TRIP_ISSUE.value: [
            "trip", "ride", "journey", "route",
            "destination", "drop off", "dropoff"
        ]
    }

    def __init__(self, custom_keywords: Optional[Dict[str, List[str]]] = None):
        self.keywords = custom_keywords or self.INTENT_KEYWORDS

    def get_scores(self, text: str) -> Dict[str, int]:
        """Compute keyword hit scores for each intent."""
        text_lower = str(text).lower()
        scores: Dict[str, int] = {}

        for intent, kws in self.keywords.items():
            score = sum(1 for kw in kws if kw in text_lower)
            scores[intent] = score

        return scores

    def classify(self, text: str) -> str:
        """Classify customer text into one of the 10 target intents."""
        scores = self.get_scores(text)
        best_intent = max(scores, key=scores.get)

        if scores[best_intent] == 0:
            return Intent.OTHER_SUPPORT_ISSUE.value

        return best_intent
