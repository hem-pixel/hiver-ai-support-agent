from pathlib import Path
from typing import List, Optional
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models import RetrievalResult
from app.classifier import IntentClassifier


class ResolutionRetriever:
    """Historical resolution retriever using intent-filtered TF-IDF similarity."""

    def __init__(self, data_path: Optional[Path] = None, classifier: Optional[IntentClassifier] = None):
        if data_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            data_path = base_dir / "data" / "uber_resolution_demo.csv"

        if not data_path.exists():
            raise FileNotFoundError(f"Historical resolution dataset not found at: {data_path}")

        self.data_path = data_path
        self.df = pd.read_csv(self.data_path)
        self.df["customer_message"] = self.df["customer_message"].fillna("")
        self.df["support_response"] = self.df["support_response"].fillna("")

        self.classifier = classifier or IntentClassifier()

    def retrieve(
        self,
        query: str,
        intent: Optional[str] = None,
        top_k: int = 1
    ) -> List[RetrievalResult]:
        """Retrieve top_k historical resolutions similar to the query.

        If intent is not provided, it is classified automatically.
        Filtering by intent ensures high contextual relevance before similarity ranking.
        """
        if intent is None:
            intent = self.classifier.classify(query)

        filtered = self.df[self.df["historical_intent"] == intent].copy()

        # Fallback to full dataset if no historical pairs match this intent
        if len(filtered) == 0:
            filtered = self.df.copy()

        if len(filtered) == 0 or query.strip() == "":
            return []

        # Use min_df=1 for small subsets to avoid empty vocabulary errors
        min_df = 1 if len(filtered) < 10 else 2

        try:
            vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
                min_df=min_df,
                sublinear_tf=True
            )
            vectors = vectorizer.fit_transform(filtered["customer_message"])
            query_vector = vectorizer.transform([query])
        except ValueError:
            # Fallback if vocabulary is empty with stop words
            vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 1))
            vectors = vectorizer.fit_transform(filtered["customer_message"])
            query_vector = vectorizer.transform([query])

        scores = cosine_similarity(query_vector, vectors)[0]
        top_k = min(top_k, len(filtered))
        top_indices = scores.argsort()[-top_k:][::-1]

        results: List[RetrievalResult] = []
        for index in top_indices:
            row = filtered.iloc[index]
            sim_score = round(float(scores[index]), 4)
            results.append(
                RetrievalResult(
                    intent=intent,
                    similarity=sim_score,
                    customer_message=str(row["customer_message"]),
                    support_response=str(row["support_response"])
                )
            )

        return results
