from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "uber_resolution_labeled.csv"

print("Loading historical resolutions...")

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Missing historical resolution dataset: {DATA_PATH}\n"
        "Run the data preparation script first."
    )

df = pd.read_csv(DATA_PATH)
df["customer_message"] = df["customer_message"].fillna("")
df["support_response"] = df["support_response"].fillna("")

def classify_intent(text):
    text = str(text).lower()

    rules = {
        "uber_eats_issue": ["uber eats", "eats", "food", "restaurant", "delivery", "order"],
        "account_access_issue": ["account", "login", "log in", "password", "locked", "deactivated", "sign in"],
        "driver_issue": ["driver", "pickup", "pick up", "rude", "speeding", "seat belt"],
        "cancellation_issue": ["cancel", "cancelled", "canceled", "cancellation"],
        "refund_request": ["refund", "money back", "reimburse"],
        "fare_or_charge_issue": ["fare", "charged", "charge", "overcharged", "expensive", "price", "surge"],
        "payment_issue": ["payment", "card", "cash", "credit card", "debit card", "billing"],
        "app_or_technical_issue": ["app", "error", "crash", "bug", "not working", "technical", "website"],
        "trip_issue": ["trip", "ride", "journey", "route", "destination"]
    }

    scores = {}

    for intent, keywords in rules.items():
        scores[intent] = sum(keyword in text for keyword in keywords)

    best_intent = max(scores, key=scores.get)

    if scores[best_intent] == 0:
        return "other_support_issue"

    return best_intent


print(f"Loaded {len(df):,} resolution pairs.")


def retrieve(query, top_k=3):
    intent = classify_intent(query)

    filtered = df[df["historical_intent"] == intent].copy()

    if len(filtered) == 0:
        filtered = df.copy()

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True
    )

    vectors = vectorizer.fit_transform(filtered["customer_message"])
    query_vector = vectorizer.transform([query])

    scores = cosine_similarity(query_vector, vectors)[0]

    top_indices = scores.argsort()[-top_k:][::-1]

    results = []

    for index in top_indices:
        row = filtered.iloc[index]

        results.append({
            "intent": intent,
            "similarity": round(float(scores[index]), 4),
            "customer_message": row["customer_message"],
            "support_response": row["support_response"]
        })

    return results


if __name__ == "__main__":
    query = input("\nEnter a customer message: ")

    results = retrieve(query)

    print("\n" + "=" * 70)
    print("INTENT-FILTERED HISTORICAL RESOLUTIONS")
    print("=" * 70)

    print(f"\nPredicted intent: {results[0]['intent']}")

    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Similarity: {result['similarity']}")

        print("\nCustomer:")
        print(result["customer_message"])

        print("\nUber Support:")
        print(result["support_response"])