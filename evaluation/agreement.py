import sys
from pathlib import Path
import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "evaluation" / "results"
LLM_RESULTS_PATH = RESULTS_DIR / "llm_judge_results.csv"
HUMAN_TEMPLATE_PATH = REPO_ROOT / "evaluation" / "human_judge_template.csv"
METRICS_PATH = RESULTS_DIR / "agreement_metrics.txt"
REPORT_PATH = RESULTS_DIR / "agreement_report.md"


def bin_score(score: float) -> str:
    """Convert overall score into ordinal quality bins:
    1-2 = Poor, 3 = Acceptable, 4-5 = Good.
    """
    if pd.isna(score):
        return "Unknown"
    val = round(score)
    if val <= 2:
        return "Poor"
    elif val == 3:
        return "Acceptable"
    else:
        return "Good"


def run_agreement_analysis():
    print("=" * 70)
    print("LLM JUDGE — HUMAN ANNOTATOR AGREEMENT ANALYSIS")
    print("=" * 70)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if not HUMAN_TEMPLATE_PATH.exists():
        msg = f"Error: Human judge template missing at {HUMAN_TEMPLATE_PATH}"
        print(msg)
        return

    df_human = pd.read_csv(HUMAN_TEMPLATE_PATH)

    human_cols = [
        "relevance_human",
        "groundedness_human",
        "helpfulness_human",
        "professional_tone_human",
        "safety_human",
        "overall_human"
    ]

    has_human_ratings = False
    for col in human_cols:
        if col in df_human.columns and df_human[col].dropna().count() > 0:
            has_human_ratings = True
            break

    if not has_human_ratings:
        msg = "Human ratings are not available yet; agreement cannot be calculated."
        print(f"\n{msg}")
        print("Annotators must first complete manual ratings in 'evaluation/human_judge_template.csv'.")
        print("In accordance with evaluation integrity rules, agreement scores are NOT fabricated.")

        with open(METRICS_PATH, "w", encoding="utf-8") as f:
            f.write(msg + "\n")

        report_content = """# LLM Judge & Human Annotator Agreement Report

## Status
Agreement analysis is pending manual human annotation.

## Evaluation Protocol
- **Sample Size**: 30 fixed interaction examples (`evaluation/results/judge_sample.csv`, random seed 42)
- **Criteria Evaluated**: Relevance, Groundedness, Helpfulness, Professional Tone, Safety (1–5 scale)
- **Planned Metrics**:
  - Pearson Correlation (linear alignment of overall scores)
  - Spearman Correlation (rank-order agreement)
  - Mean Absolute Error (MAE)
  - Cohen's Kappa on binned categories (1–2: Poor, 3: Acceptable, 4–5: Good)
- **Integrity Guarantee**: Agreement statistics require genuine completed paired ratings. No synthetic human scores or fabricated correlations are produced.
"""
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(report_content)
        return

    if not LLM_RESULTS_PATH.exists():
        msg = f"LLM judge results not found at {LLM_RESULTS_PATH}. Run llm_judge.py first."
        print(f"\n{msg}")
        with open(METRICS_PATH, "w", encoding="utf-8") as f:
            f.write(msg + "\n")
        return

    df_llm = pd.read_csv(LLM_RESULTS_PATH)
    if len(df_llm) == 0 or "overall_score" not in df_llm.columns or df_llm["overall_score"].dropna().count() == 0:
        msg = "LLM judge results contain no valid scores (API quota unavailable). Agreement cannot be calculated."
        print(f"\n{msg}")
        with open(METRICS_PATH, "w", encoding="utf-8") as f:
            f.write(msg + "\n")
        return

    # Merge on customer_tweet_id
    merged = pd.merge(
        df_llm[["customer_tweet_id", "overall_score"]],
        df_human[["customer_tweet_id", "overall_human"]],
        on="customer_tweet_id",
        how="inner"
    ).dropna(subset=["overall_score", "overall_human"])

    paired_count = len(merged)
    if paired_count < 2:
        msg = "Insufficient paired ratings for agreement analysis."
        print(f"\n{msg} (Found {paired_count} paired rows, need >= 2)")
        with open(METRICS_PATH, "w", encoding="utf-8") as f:
            f.write(msg + "\n")
        return

    from scipy.stats import pearsonr, spearmanr
    from sklearn.metrics import cohen_kappa_score

    p_corr, p_val = pearsonr(merged["overall_score"], merged["overall_human"])
    s_corr, s_val = spearmanr(merged["overall_score"], merged["overall_human"])
    mae = float(np.mean(np.abs(merged["overall_score"] - merged["overall_human"])))

    # Ordinal binning for Cohen's Kappa
    llm_binned = merged["overall_score"].apply(bin_score)
    human_binned = merged["overall_human"].apply(bin_score)
    kappa = cohen_kappa_score(llm_binned, human_binned, labels=["Poor", "Acceptable", "Good"])

    metrics_text = f"""======================================================================
LLM JUDGE — HUMAN ANNOTATOR AGREEMENT METRICS
======================================================================
Paired Ratings:       {paired_count}
Pearson Correlation:  {p_corr:.4f} (p-value: {p_val:.4e})
Spearman Correlation: {s_corr:.4f} (p-value: {s_val:.4e})
Mean Absolute Error:  {mae:.4f}
Cohen's Kappa (bins): {kappa:.4f}
"""
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        f.write(metrics_text)

    print("\n" + metrics_text)

    report_text = f"""# LLM Judge & Human Annotator Agreement Report

- **Paired Evaluations**: {paired_count}
- **Pearson Correlation**: `{p_corr:.4f}`
- **Spearman Correlation**: `{s_corr:.4f}`
- **Mean Absolute Error (MAE)**: `{mae:.4f}`
- **Cohen's Kappa**: `{kappa:.4f}`

## Interpretation
- Pearson correlation evaluates linear scaling agreement between LLM and human scores.
- Spearman correlation evaluates rank consistency of response quality.
- Cohen's Kappa evaluates categorical agreement across ordinal tiers (Poor, Acceptable, Good).
"""
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Saved agreement report to: {REPORT_PATH}")


if __name__ == "__main__":
    run_agreement_analysis()
