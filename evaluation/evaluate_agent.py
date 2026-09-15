import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# Setup repo paths
REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
DATA_PATH = REPO_ROOT / "data" / "golden_set.csv"
RESULTS_DIR = REPO_ROOT / "evaluation" / "results"

for p in [str(REPO_ROOT), str(BACKEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.services.support_agent import analyze_customer_message

# Standard 10-intent taxonomy
INTENT_TAXONOMY = [
    "account_access_issue",
    "app_or_technical_issue",
    "cancellation_issue",
    "driver_issue",
    "fare_or_charge_issue",
    "other_support_issue",
    "payment_issue",
    "refund_request",
    "trip_issue",
    "uber_eats_issue"
]


def run_evaluation():
    print("=" * 75)
    print("HIVER AI SUPPORT AGENT - GOLDEN EVALUATION HARNESS")
    print("=" * 75)

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Golden dataset missing: {DATA_PATH}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df_gold = pd.read_csv(DATA_PATH)
    print(f"Loaded golden set: {len(df_gold)} examples from {DATA_PATH.name}")

    records = []
    print("\nRunning agent pipeline over all golden examples (NO gold labels leaked to model)...")

    for idx, row in df_gold.iterrows():
        customer_tweet_id = row.get("tweet_id")
        customer_message = str(row.get("text") if pd.notna(row.get("text")) else "")
        gold_intent = str(row.get("gold_intent")).strip()

        # Run pipeline using ONLY customer_message
        res = analyze_customer_message(customer_message)

        pred_intent = res["intent"]
        confidence = res["confidence"]  # None
        similarity = float(res.get("similarity", 0.0))
        hist_match = res.get("historical_match")
        draft_reply = res.get("draft_reply", "")
        decision = res.get("decision", "ESCALATE")
        decision_reason = res.get("decision_reason", "")

        records.append({
            "customer_tweet_id": customer_tweet_id,
            "customer_message": customer_message,
            "gold_intent": gold_intent,
            "predicted_intent": pred_intent,
            "confidence": confidence,
            "similarity": similarity,
            "historical_match": json.dumps(hist_match) if hist_match else None,
            "draft_reply": draft_reply,
            "decision": decision,
            "decision_reason": decision_reason
        })

    df_preds = pd.DataFrame(records)
    preds_path = RESULTS_DIR / "agent_predictions.csv"
    df_preds.to_csv(preds_path, index=False)
    print(f"Saved predictions to: {preds_path}")

    # 1. Classification Metrics
    y_true = df_preds["gold_intent"]
    y_pred = df_preds["predicted_intent"]

    accuracy = accuracy_score(y_true, y_pred)
    macro_prec = precision_score(y_true, y_pred, average="macro", zero_division=0)
    macro_rec = recall_score(y_true, y_pred, average="macro", zero_division=0)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    clf_report_dict = classification_report(
        y_true,
        y_pred,
        labels=INTENT_TAXONOMY,
        output_dict=True,
        zero_division=0
    )
    df_report = pd.DataFrame(clf_report_dict).transpose()
    report_csv_path = RESULTS_DIR / "classification_report.csv"
    df_report.to_csv(report_csv_path)

    metrics_text = f"""======================================================================
HIVER AI SUPPORT AGENT — CLASSIFICATION METRICS
======================================================================
Total Examples Evaluated: {len(df_preds)}
Accuracy:                {accuracy:.4f} ({accuracy * 100:.2f}%)
Macro Precision:         {macro_prec:.4f}
Macro Recall:            {macro_rec:.4f}
Macro F1:                {macro_f1:.4f}
Weighted F1:             {weighted_f1:.4f}

----------------------------------------------------------------------
PER-INTENT CLASSIFICATION BREAKDOWN
----------------------------------------------------------------------
{classification_report(y_true, y_pred, labels=INTENT_TAXONOMY, zero_division=0)}
"""
    metrics_txt_path = RESULTS_DIR / "classification_metrics.txt"
    with open(metrics_txt_path, "w", encoding="utf-8") as f:
        f.write(metrics_text)

    print("\n" + metrics_text)

    # 2. Confusion Matrix (Exact 10-intent taxonomy)
    cm = confusion_matrix(y_true, y_pred, labels=INTENT_TAXONOMY)
    df_cm = pd.DataFrame(cm, index=INTENT_TAXONOMY, columns=INTENT_TAXONOMY)
    cm_path = RESULTS_DIR / "confusion_matrix.csv"
    df_cm.to_csv(cm_path)
    print(f"Saved confusion matrix to: {cm_path}")

    # 3. Decision Metrics
    total = len(df_preds)
    decision_counts = df_preds["decision"].value_counts()
    auto_count = decision_counts.get("AUTO_HANDLE", 0)
    esc_count = decision_counts.get("ESCALATE", 0)
    auto_pct = (auto_count / total) * 100
    esc_pct = (esc_count / total) * 100

    decision_crosstab = pd.crosstab(
        df_preds["gold_intent"],
        df_preds["decision"],
        margins=True,
        margins_name="Total"
    )
    decision_csv_path = RESULTS_DIR / "decision_metrics.csv"
    decision_crosstab.to_csv(decision_csv_path)
    print(f"Saved decision metrics to: {decision_csv_path}")

    print("\n" + "=" * 50)
    print("ROUTING DECISION DISTRIBUTION")
    print("=" * 50)
    print(f"AUTO_HANDLE: {auto_count} ({auto_pct:.2f}%)")
    print(f"ESCALATE:    {esc_count} ({esc_pct:.2f}%)")

    # 4. Retrieval Analysis
    has_match_series = df_preds["historical_match"].notna()
    match_count = has_match_series.sum()
    match_pct = (match_count / total) * 100

    similarities = df_preds.loc[has_match_series, "similarity"]
    mean_sim = similarities.mean() if len(similarities) > 0 else 0.0
    median_sim = similarities.median() if len(similarities) > 0 else 0.0

    below_threshold_count = (df_preds["similarity"] < 0.20).sum()
    below_threshold_pct = (below_threshold_count / total) * 100

    no_match_count = total - match_count
    no_match_pct = (no_match_count / total) * 100

    retrieval_text = f"""======================================================================
HISTORICAL RETRIEVAL ANALYSIS
======================================================================
Total Evaluated:                  {total}
Matches Found:                    {match_count} ({match_pct:.2f}%)
No Match Found (sim <= 0.0):      {no_match_count} ({no_match_pct:.2f}%)
Mean Similarity (matches):        {mean_sim:.4f}
Median Similarity (matches):      {median_sim:.4f}
Below 0.20 Threshold:             {below_threshold_count} ({below_threshold_pct:.2f}%)
"""
    retrieval_txt_path = RESULTS_DIR / "retrieval_metrics.txt"
    with open(retrieval_txt_path, "w", encoding="utf-8") as f:
        f.write(retrieval_text)
    print("\n" + retrieval_text)


if __name__ == "__main__":
    run_evaluation()
