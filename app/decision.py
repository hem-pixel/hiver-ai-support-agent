from typing import Optional, List
from app.models import Action, AgentDecision, Intent, RetrievalResult


class DecisionEngine:
    """Evaluates support resolution context to decide between AUTO_HANDLE and ESCALATE."""

    DEFAULT_ESCALATION_PHRASES: List[str] = [
        "send us a dm",
        "send us a note",
        "contact us",
        "direct messages",
        "send us a message",
        "reach out via dm",
        "follow up via dm"
    ]

    def __init__(
        self,
        similarity_threshold: float = 0.20,
        escalation_phrases: Optional[List[str]] = None
    ):
        self.similarity_threshold = similarity_threshold
        self.escalation_phrases = escalation_phrases or self.DEFAULT_ESCALATION_PHRASES

    def decide(
        self,
        intent: str,
        retrieval: Optional[RetrievalResult]
    ) -> AgentDecision:
        """Decide whether to AUTO_HANDLE or ESCALATE with justification."""
        if retrieval is None:
            return AgentDecision(
                action=Action.ESCALATE,
                reason="No historical resolution could be retrieved."
            )

        response_lower = retrieval.support_response.lower()

        # Check if historical response requires direct human intervention
        if any(phrase in response_lower for phrase in self.escalation_phrases):
            return AgentDecision(
                action=Action.ESCALATE,
                reason="Historical responses indicate that this issue requires direct support follow-up."
            )

        # Check similarity confidence
        if retrieval.similarity < self.similarity_threshold:
            return AgentDecision(
                action=Action.ESCALATE,
                reason=f"Similarity score ({retrieval.similarity:.4f}) is below threshold ({self.similarity_threshold:.2f})."
            )

        # Safety policy: Account deactivation / access issues typically require human verification
        if intent == Intent.ACCOUNT_ACCESS_ISSUE.value and "deactivated" in retrieval.customer_message.lower():
            return AgentDecision(
                action=Action.ESCALATE,
                reason="Account access and deactivation inquiries require human agent identity verification."
            )

        return AgentDecision(
            action=Action.AUTO_HANDLE,
            reason=f"A sufficiently similar historical resolution was found (similarity: {retrieval.similarity:.4f})."
        )

    def draft_reply(
        self,
        intent: str,
        retrieval: Optional[RetrievalResult]
    ) -> str:
        """Generate a grounded, professional draft response for the customer."""
        if retrieval and retrieval.support_response:
            resp_lower = retrieval.support_response.lower()
            if "send us a note" in resp_lower or "send us a dm" in resp_lower or "contact us" in resp_lower:
                return (
                    "Sorry about the issue you're experiencing. "
                    "Please send us a DM with your details so our support team "
                    "can review this and assist you further."
                )

        intent_templates = {
            Intent.REFUND_REQUEST.value: (
                "Sorry about the inconvenience. "
                "Please share your trip details with our support team so we can review your refund request."
            ),
            Intent.FARE_OR_CHARGE_ISSUE.value: (
                "Sorry about the unexpected charge. "
                "Please send us your trip details so our support team can review the fare and assist you."
            ),
            Intent.DRIVER_ISSUE.value: (
                "We apologize for the negative experience with your driver. "
                "Please share your trip details so our safety and operations team can address this."
            ),
            Intent.UBER_EATS_ISSUE.value: (
                "We are sorry for the trouble with your order. "
                "Please provide your order details so our team can help resolve this delivery issue."
            ),
            Intent.CANCELLATION_ISSUE.value: (
                "We understand your frustration regarding this cancellation. "
                "Please share your trip details so we can check the cancellation fee and assist you."
            ),
            Intent.ACCOUNT_ACCESS_ISSUE.value: (
                "We understand you are having trouble accessing your account. "
                "Please reach out with your registered email and phone number so we can securely assist you."
            ),
            Intent.PAYMENT_ISSUE.value: (
                "We are sorry for the payment difficulty. "
                "Please verify your payment method or contact us so we can review this transaction."
            ),
            Intent.APP_OR_TECHNICAL_ISSUE.value: (
                "We apologize for the technical issue. "
                "Please make sure your app is updated to the latest version or reply with details so we can investigate."
            ),
            Intent.TRIP_ISSUE.value: (
                "We're sorry to hear about the problem with your trip. "
                "Please share your trip details so we can review what happened."
            )
        }

        return intent_templates.get(
            intent,
            "Sorry you're experiencing this issue. Please contact our support team with your details so we can assist you."
        )
