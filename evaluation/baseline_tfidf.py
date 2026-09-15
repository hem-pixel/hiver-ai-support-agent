import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

PATH = r"D:\twcs\hiver_data\golden_set.csv"

df = pd.read_csv(PATH)

df = df.dropna(subset=["text", "gold_intent"])

X = df["text"]
y = df["gold_intent"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True
    )),
    ("classifier", LogisticRegression(
        max_iter=2000
    ))
])

model.fit(X_train, y_train)

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("=" * 70)
print("TF-IDF + LOGISTIC REGRESSION BASELINE")
print("=" * 70)

print(f"Training examples: {len(X_train)}")
print(f"Test examples:     {len(X_test)}")
print(f"Accuracy:          {accuracy:.4f}")
print(f"Accuracy %:        {accuracy * 100:.2f}%")

print("\n" + "=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)

print("\n" + "=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

labels = sorted(y.unique())

cm = confusion_matrix(
    y_test,
    predictions,
    labels=labels
)

print(
    pd.DataFrame(
        cm,
        index=labels,
        columns=labels
    )
)