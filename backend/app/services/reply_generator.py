import re
from typing import Optional, Dict, Any


def clean_tweet_text(text: str) -> str:
    """Remove raw Twitter handles and dead short links from historical text."""
    if not text:
        return ""
    # Remove @mentions
    cleaned = re.sub(r"@\w+", "", text)
    # Remove t.co or http/https URLs
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    # Clean whitespace and stray punctuation
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"^[;,\.\s]+", "", cleaned)
    return cleaned


def generate_draft_reply(
    intent: str,
    historical_match: Optional[Dict[str, str]],
    similarity: float
) -> str:
    """Generate a grounded, professional draft response based on historical resolution patterns.

    - Acknowledges customer's specific issue
    - Grounds action in the historical support response pattern
    - Avoids inventing false guarantees, refunds, or policies
    - Employs safe fallback when historical match is weak (< 0.20) or absent
    """
    # Safe fallback when similarity is below threshold or no match exists
    if not historical_match or similarity < 0.20:
        intent_fallbacks = {
            "fare_or_charge_issue": (
                "Sorry to hear about the issue with your fare. "
                "Please share your trip date and details with our support team so we can review the charge."
            ),
            "refund_request": (
                "We understand you are requesting a refund. "
                "Please share your trip details and receipt info so our support team can review your request."
            ),
            "driver_issue": (
                "We take driver feedback very seriously. "
                "Please provide your trip details so our safety and operations team can address this situation."
            ),
            "uber_eats_issue": (
                "We apologize for the trouble with your delivery order. "
                "Please share your order number and restaurant details so our support team can assist."
            ),
            "cancellation_issue": (
                "We understand your concern regarding the cancellation. "
                "Please share your trip details so our team can check the cancellation status."
            ),
            "account_access_issue": (
                "We apologize for the difficulty accessing your account. "
                "Please confirm your registered email and phone number so our account team can assist you safely."
            ),
            "payment_issue": (
                "Sorry for the payment difficulty. "
                "Please review your active payment method in the app or contact support with transaction details."
            ),
            "app_or_technical_issue": (
                "We apologize for the technical issue with the app. "
                "Please ensure your app is updated to the latest version, or share your device details so we can investigate."
            ),
            "trip_issue": (
                "Sorry to hear about the problem with your trip. "
                "Please provide your trip details so our support team can look into what happened."
            )
        }
        return intent_fallbacks.get(
            intent,
            "Sorry you're experiencing this issue. Please contact our support team with your details so we can assist you."
        )

    # Resolution Pattern Extraction from Historical Response
    raw_support = historical_match.get("support_response", "")
    support_lower = raw_support.lower()

    # Pattern A: Historical response asked customer for direct follow-up / DM / note
    if any(phrase in support_lower for phrase in [
        "send us a note", "send us a dm", "contact us", "dm us",
        "reach out via dm", "direct message", "send us a message", "get in touch"
    ]):
        if intent == "fare_or_charge_issue":
            return (
                "Sorry about the unexpected charge on your ride. "
                "Please send us a direct message with your trip details so our support team can review the fare."
            )
        if intent == "refund_request":
            return (
                "Sorry about the inconvenience with your ride. "
                "Please send us a DM with your trip details so our team can review your refund request."
            )
        if intent == "driver_issue":
            return (
                "We sincerely apologize for the experience with your driver. "
                "Please send us a direct message with your trip details so our team can follow up immediately."
            )
        if intent == "uber_eats_issue":
            return (
                "We are sorry for the trouble with your delivery order. "
                "Please send us a DM with your order details so our team can look into this right away."
            )
        if intent == "account_access_issue":
            return (
                "We understand you are having trouble with your account. "
                "Please send us a DM with your registered email and phone number so we can securely assist you."
            )
        return (
            "Sorry about the issue you're experiencing. "
            "Please send us a DM with your details so our support team can review this and assist you further."
        )

    # Pattern B: In-app self-serve / Help navigation guidance
    if "help" in support_lower or "app" in support_lower or "receipt" in support_lower:
        cleaned_guidance = clean_tweet_text(raw_support)
        if len(cleaned_guidance) > 20:
            return (
                f"We are here to help. Based on standard resolution procedures: {cleaned_guidance} "
                "If you need further assistance, please let us know."
            )

    # Pattern C: Standard intent-grounded response
    if intent == "account_access_issue":
        return (
            "We understand you are having difficulty accessing your account. "
            "Please verify your credentials or contact support so our team can verify your identity and assist."
        )

    return (
        "Thank you for contacting support. We have reviewed your inquiry against our historical resolutions. "
        "Please provide your trip or order details so we can assist you with this issue."
    )
