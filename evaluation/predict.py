from pathlib import Path
import pandas as pd
import json
import time
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent
GOLDEN_PATH = BASE_DIR / "data" / "golden_set.csv"
OUTPUT_PATH = BASE_DIR / "data" / "golden_predictions.csv"


MODEL = "gemini-3.5-flash"

INTENTS = [
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

client = genai.Client()

gold = pd.read_csv(GOLDEN_PATH)

try:
    predictions = pd.read_csv(OUTPUT_PATH)
except FileNotFoundError:
    predictions = pd.DataFrame(
        columns=["tweet_id", "predicted_intent"]
    )

done = set(predictions["tweet_id"].astype(str))

pending = gold[
    ~gold["tweet_id"].astype(str).isin(done)
]

print("=" * 70)
print("FRESH GOLDEN-SET PREDICTION")
print("=" * 70)
print(f"Total examples: {len(gold)}")
print(f"Already predicted: {len(done)}")
print(f"Pending: {len(pending)}")

for count, (_, row) in enumerate(pending.iterrows(), 1):

    prompt = f"""
You are a customer support intent classifier for Uber.

Classify the customer message into exactly ONE of these intents:

{json.dumps(INTENTS)}

Return ONLY valid JSON:
{{"intent": "one_intent_from_list"}}

Customer message:
{row['text']}
"""

    success = False

    while not success:

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            text = response.text.strip()
            text = text.replace("```json", "").replace("```", "").strip()

            result = json.loads(text)
            intent = result["intent"]

            if intent not in INTENTS:
                raise ValueError(f"Invalid intent: {intent}")

            predictions.loc[len(predictions)] = [
                row["tweet_id"],
                intent
            ]

            predictions.to_csv(
                OUTPUT_PATH,
                index=False
            )

            print(
                f"Predicted {len(predictions)}/200: {intent}"
            )

            success = True

            # Stay safely below the 5 requests/minute limit.
            time.sleep(13)

        except Exception as e:

            error_text = str(e)

            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:

                print("\nRate limit reached.")
                print("Waiting 65 seconds before retrying...\n")

                time.sleep(65)

            else:

                print(f"Error: {e}")
                print("Waiting 10 seconds...")
                time.sleep(10)

print("\n" + "=" * 70)
print("PREDICTION COMPLETE")
print("=" * 70)
print(f"Predictions: {len(predictions)}")
print(f"Saved: {OUTPUT_PATH}")