import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

GOLDEN_PATH = r"D:\twcs\hiver_data\golden_set.csv"
PREDICTION_PATH = r"D:\twcs\hiver_data\golden_predictions.csv"

gold = pd.read_csv(GOLDEN_PATH)
pred = pd.read_csv(PREDICTION_PATH)

df = gold[["tweet_id", "text", "gold_intent"]].merge(
    pred[["tweet_id", "predicted_intent"]],
    on="tweet_id",
    how="inner"
)

df = df.dropna(subset=["gold_intent", "predicted_intent"])

y_true = df["gold_intent"]
y_pred = df["predicted_intent"]

print("=" * 70)
print("HIVER AI SUPPORT AGENT EVALUATION")
print("=" * 70)

print(f"Evaluation examples: {len(df)}")

accuracy = accuracy_score(y_true, y_pred)

print(f"\nAccuracy: {accuracy:.4f}")
print(f"Accuracy %: {accuracy * 100:.2f}%")

print("\n" + "=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

print(
    classification_report(
        y_true,
        y_pred,
        zero_division=0
    )
)

print("\n" + "=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

labels = sorted(y_true.unique())

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=labels
)

print(pd.DataFrame(cm, index=labels, columns=labels))

print("\n" + "=" * 70)
print("RESULT")
print("=" * 70)

correct = (y_true == y_pred).sum()
wrong = (y_true != y_pred).sum()

print(f"Correct: {correct}")
print(f"Wrong:   {wrong}")
