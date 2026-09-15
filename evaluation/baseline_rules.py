from pathlib import Path
import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "golden_set.csv"


INTENT_KEYWORDS = {
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


def classify(text):
    text = str(text).lower()
    scores = {}

    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0

        for keyword in keywords:
            if keyword in text:
                score += 1

        scores[intent] = score

    best_intent = max(scores, key=scores.get)

    if scores[best_intent] == 0:
        return "other_support_issue"

    return best_intent


df = pd.read_csv(DATA_PATH)

X = df["text"].fillna("")
y = df["gold_intent"]

_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

predictions = X_test.apply(classify)

print("=" * 60)
print("RULE-BASED BASELINE")
print("=" * 60)

print(f"Test samples: {len(X_test)}")

accuracy = accuracy_score(y_test, predictions)

print(f"\nAccuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)

print("\nConfusion Matrix:")
labels = sorted(y.unique())

cm = confusion_matrix(
    y_test,
    predictions,
    labels=labels
)

print(pd.DataFrame(
    cm,
    index=labels,
    columns=labels
))