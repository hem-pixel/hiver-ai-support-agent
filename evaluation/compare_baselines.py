import pandas as pd

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
    r"D:\twcs\evaluation\baseline_results.csv",
    index=False
)

print("\nSaved:")
print(r"D:\twcs\evaluation\baseline_results.csv")