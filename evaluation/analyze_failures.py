from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "evaluation" / "results"
PREDS_PATH = RESULTS_DIR / "agent_predictions.csv"
OUTPUT_MD = RESULTS_DIR / "failure_analysis.md"


def analyze_failures():
    if not PREDS_PATH.exists():
        raise FileNotFoundError(
            f"Predictions file not found: {PREDS_PATH}. Run evaluate_agent.py first."
        )

    df = pd.read_csv(PREDS_PATH)
    failures = df[df["gold_intent"] != df["predicted_intent"]].copy()

    total_examples = len(df)
    total_failures = len(failures)
    error_rate = (total_failures / total_examples) * 100

    print("=" * 70)
    print("HIVER AI SUPPORT AGENT - FAILURE ANALYSIS")
    print("=" * 70)
    print(f"Total Examples:  {total_examples}")
    print(f"Total Failures:  {total_failures} ({error_rate:.2f}% error rate)")
    print(f"Total Correct:   {total_examples - total_failures} ({100 - error_rate:.2f}% accuracy)")

    # Group by (gold_intent, predicted_intent)
    pair_counts = (
        failures.groupby(["gold_intent", "predicted_intent"])
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )

    top_patterns = pair_counts.head(5)

    md_content = f"""# Failure Analysis Report: Hiver AI Support Agent

- **Dataset**: `data/golden_set.csv` (200 human-verified examples)
- **Total Inquiries Evaluated**: {total_examples}
- **Misclassified Cases**: {total_failures}
- **Observed Accuracy**: {100 - error_rate:.2f}%

---

## Executive Summary

The failure analysis reveals that classification errors predominantly concentrate around overlapping intent vocabularies (e.g., fare disputes requesting refunds, payment card failures overlapping with trip charges) and general conversational inquiries falling into or out of `other_support_issue`.

---

## Top 5 Classification Failure Patterns

"""

    hypotheses_map = {
        ("fare_or_charge_issue", "refund_request"): (
            "Customer messages complaining about overcharges frequently use explicit words like 'refund' or 'money back', "
            "triggering the refund rule before or above fare dispute keywords."
        ),
        ("refund_request", "fare_or_charge_issue"): (
            "Customers seeking refunds for ride issues mention 'fare' or 'charged', causing the fare rule to override refund intent."
        ),
        ("payment_issue", "fare_or_charge_issue"): (
            "Billing and credit card failures often describe being 'charged' or 'overcharged', blurring the boundary between payment transaction issues and trip fare disputes."
        ),
        ("trip_issue", "driver_issue"): (
            "Trip routing problems, pickups, and dropoff delays frequently reference the driver in the context of the journey, triggering driver issue keywords."
        ),
        ("app_or_technical_issue", "account_access_issue"): (
            "App login crashes or authentication errors contain account-related terms ('sign in', 'login') that trigger account access instead of app technical errors."
        ),
        ("other_support_issue", "driver_issue"): (
            "General customer complaints mentioning the word 'driver' or 'ride' without a specific operational breakdown trigger the broad driver keyword baseline."
        ),
        ("cancellation_issue", "fare_or_charge_issue"): (
            "Disputes over cancellation fees often emphasize the 'fee' or 'charged' aspect rather than the cancellation itself."
        )
    }

    for idx, row in top_patterns.iterrows():
        gold = row["gold_intent"]
        pred = row["predicted_intent"]
        cnt = row["count"]

        # Find real representative examples
        examples = failures[
            (failures["gold_intent"] == gold) & (failures["predicted_intent"] == pred)
        ].head(2)

        hypo = hypotheses_map.get(
            (gold, pred),
            f"Overlapping terminology between '{gold}' and '{pred}' where keywords from '{pred}' dominate the hit scoring."
        )

        md_content += f"""### Pattern #{idx + 1}: Gold `{gold}` → Predicted `{pred}` ({cnt} instances)

- **Failure Count**: {cnt} examples
- **Root Cause Hypothesis**: {hypo}

**Observed Examples from Golden Set**:
"""
        for e_idx, (_, ex) in enumerate(examples.iterrows(), 1):
            msg = ex["customer_message"].replace("\n", " ").strip()
            sim = ex["similarity"]
            md_content += f"""
{e_idx}. **Message**: *"{msg}"*
   - **Similarity Score**: `{sim:.4f}`
   - **Routing Decision**: `{ex['decision']}`
"""
        md_content += "\n---\n\n"

    md_content += """## Recommendations for Model Iteration

1. **Hierarchical or Multi-label Intent Disambiguation**:
   Decouple root causes (e.g. `fare_or_charge_issue`) from remediation actions (e.g. `refund_request`).
2. **Context-Aware Semantic Embeddings**:
   Augment keyword scoring with dense embeddings (e.g. Sentence-BERT or fine-tuned LLM) to capture semantic intent beyond surface n-grams.
3. **Dedicated Financial Intent Boundary**:
   Introduce disambiguation logic specifically separating payment gateway failures (`payment_issue`) from trip pricing adjustments (`fare_or_charge_issue`).
"""

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\nSaved failure analysis to: {OUTPUT_MD}")
    print("\nTop Failure Patterns:")
    for _, r in top_patterns.iterrows():
        print(f"  {r['gold_intent']} -> {r['predicted_intent']}: {r['count']} cases")


if __name__ == "__main__":
    analyze_failures()
