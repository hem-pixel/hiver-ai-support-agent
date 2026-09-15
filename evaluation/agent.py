from retriever import retrieve

def decide_action(intent, similarity, response):
    response_lower = response.lower()

    escalation_phrases = [
        "send us a dm",
        "send us a note",
        "contact us",
        "direct messages",
        "send us a message"
    ]

    if any(phrase in response_lower for phrase in escalation_phrases):
        return (
            "ESCALATE",
            "Historical responses indicate that this issue requires direct support follow-up."
        )

    if similarity < 0.20:
        return (
            "ESCALATE",
            "No sufficiently similar historical resolution was found."
        )

    return (
        "AUTO_HANDLE",
        "A sufficiently similar historical resolution was found."
    )


def draft_reply(intent, historical_response):
    response_lower = historical_response.lower()

    if "send us a note" in response_lower or "send us a dm" in response_lower:
        return (
            "Sorry about the issue you're experiencing. "
            "Please send us a DM with your trip details so our support team "
            "can review this and assist you further."
        )

    if intent == "refund_request":
        return (
            "Sorry about the inconvenience. "
            "Please share your trip details with our support team so we can "
            "review your refund request."
        )

    if intent == "fare_or_charge_issue":
        return (
            "Sorry about the unexpected charge. "
            "Please send us your trip details so our support team can review "
            "the fare and assist you."
        )

    return (
        "Sorry you're experiencing this issue. "
        "Please contact our support team with your details so we can assist you."
    )


def run_agent(customer_message):
    results = retrieve(customer_message, top_k=1)

    best = results[0]

    intent = best["intent"]
    similarity = best["similarity"]
    historical_customer = best["customer_message"]
    historical_response = best["support_response"]

    reply = draft_reply(intent, historical_response)

    decision, reason = decide_action(
        intent,
        similarity,
        historical_response
    )

    print("\n" + "=" * 70)
    print("AI SUPPORT AGENT")
    print("=" * 70)

    print("\nCustomer message:")
    print(customer_message)

    print("\nPredicted intent:")
    print(intent)

    print("\nBest historical similarity:")
    print(similarity)

    print("\nHistorical customer message:")
    print(historical_customer)

    print("\nHistorical support response:")
    print(historical_response)

    print("\nDraft reply:")
    print(reply)

    print("\nDecision:")
    print(decision)

    print("\nReason:")
    print(reason)


if __name__ == "__main__":
    customer_message = input("\nEnter a customer message: ")
    run_agent(customer_message)