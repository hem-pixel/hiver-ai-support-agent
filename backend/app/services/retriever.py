from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Resolve dataset path relative to repository root
BASE_DIR = Path(__file__).resolve().parents[3]
DATA_PATH = BASE_DIR / "data" / "uber_resolution_demo.csv"

# Global cached resolution dataset
_df_resolutions: Optional[pd.DataFrame] = None


def get_resolution_dataframe() -> pd.DataFrame:
    """Load and cache the historical resolution dataset."""
    global _df_resolutions
    if _df_resolutions is None:
        if not DATA_PATH.exists():
            raise FileNotFoundError(f"Historical resolution dataset missing at: {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
        df["customer_message"] = df["customer_message"].fillna("").astype(str)
        df["support_response"] = df["support_response"].fillna("").astype(str)
        _df_resolutions = df
    return _df_resolutions


def retrieve_historical_resolution(query: str, intent: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve the most relevant historical customer/support resolution.

    1. Filters historical examples by predicted intent when possible.
    2. Calculates TF-IDF cosine similarity.
    3. Returns the top relevant historical case or None if no match exists.
    4. Returns the actual un-fabricated similarity score.
    """
    clean_query = str(query or "").strip()
    if not clean_query:
        return {
            "historical_match": None,
            "similarity": 0.0
        }

    df = get_resolution_dataframe()

    # 1. Filter historical examples by intent when available
    filtered = df[df["historical_intent"] == intent].copy() if intent else df.copy()
    if len(filtered) == 0:
        filtered = df.copy()

    if len(filtered) == 0:
        return {
            "historical_match": None,
            "similarity": 0.0
        }

    # 2. Calculate TF-IDF cosine similarity
    try:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True
        )
        vectors = vectorizer.fit_transform(filtered["customer_message"])
        query_vector = vectorizer.transform([clean_query])
        scores = cosine_similarity(query_vector, vectors)[0]
    except Exception:
        # Fallback if tokenizer encounters non-standard characters
        return {
            "historical_match": None,
            "similarity": 0.0
        }

    best_index = scores.argmax()
    best_similarity = float(scores[best_index])

    # If zero overlap, do not fabricate a match
    if best_similarity <= 0.0:
        return {
            "historical_match": None,
            "similarity": 0.0,
            "nearest_candidate": None
        }

    best_row = filtered.iloc[best_index]
    candidate = {
        "customer_message": str(best_row["customer_message"]),
        "support_response": str(best_row["support_response"])
    }

    # Semantics: A historical match is only usable when similarity >= 0.20.
    # Below 0.20, expose historical_match = None while preserving similarity for diagnostics.
    usable_match = candidate if best_similarity >= 0.20 else None

    return {
        "historical_match": usable_match,
        "similarity": round(best_similarity, 4),
        "nearest_candidate": candidate
    }

