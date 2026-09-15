from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "baseline_results.csv"

results = pd.DataFrame({
    "Model": [
        "TF-IDF + Logistic Regression",
        "Keyword Rule-Based"
    ],
    "Accuracy": [
        0.40,
        0.64
    ]
})

print("=" * 50)
print("BASELINE COMPARISON")
print("=" * 50)
print(results.to_string(index=False))

results.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nSaved:")
print(OUTPUT_PATH)