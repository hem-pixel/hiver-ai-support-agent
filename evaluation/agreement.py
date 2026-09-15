from pathlib import Path
import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
LLM_RESULTS_PATH = REPO_ROOT / "evaluation" / "results" / "llm_judge_results.csv"
HUMAN_TEMPLATE_PATH = REPO_ROOT / "evaluation" / "human_judge_template.csv"


def check_and_calculate_agreement():
    print("=" * 70)
    print("LLM JUDGE - HUMAN ANNOTATOR AGREEMENT")
    print("=" * 70)

    if not HUMAN_TEMPLATE_PATH.exists():
        print(f"Error: Human judge template not found at {HUMAN_TEMPLATE_PATH}")
        return

    df_human = pd.read_csv(HUMAN_TEMPLATE_PATH)

    # Check if human ratings are populated
    human_cols = [
        "relevance_human",
        "groundedness_human",
        "helpfulness_human",
        "professional_tone_human",
        "safety_human",
        "overall_human"
    ]

    has_ratings = False
    for col in human_cols:
        if col in df_human.columns and df_human[col].dropna().count() > 0:
            has_ratings = True
            break

    if not has_ratings:
        print("\nHuman ratings are not available yet; agreement cannot be calculated.")
        print("Annotators must first fill in ratings in 'evaluation/human_judge_template.csv'.")
        print("In accordance with evaluation integrity rules, agreement scores are NOT fabricated.")
        return

    if not LLM_RESULTS_PATH.exists():
        print(f"\nLLM judge results not found at {LLM_RESULTS_PATH}. Run llm_judge.py first.")
        return

    df_llm = pd.read_csv(LLM_RESULTS_PATH)
    if len(df_llm) == 0 or "overall_score" not in df_llm.columns or df_llm["overall_score"].dropna().count() == 0:
        print("\nLLM judge results contain no valid scores (API quota unavailable). Agreement cannot be calculated.")
        return

    # Merge on customer_tweet_id
    merged = pd.merge(
        df_llm,
        df_human,
        on="customer_tweet_id",
        how="inner"
    ).dropna(subset=["overall_score", "overall_human"])

    if len(merged) < 5:
        print(f"\nInsufficient overlapping scored rows ({len(merged)}) to compute statistical correlations.")
        return

    from scipy.stats import pearsonr, spearmanr
    from sklearn.metrics import cohen_kappa_score

    p_corr, p_val = pearsonr(merged["overall_score"], merged["overall_human"])
    s_corr, s_val = spearmanr(merged["overall_score"], merged["overall_human"])

    # Binned rounded kappa
    llm_binned = np.round(merged["overall_score"]).astype(int)
    human_binned = np.round(merged["overall_human"]).astype(int)
    kappa = cohen_kappa_score(llm_binned, human_binned)

    print(f"Paired Evaluations:   {len(merged)}")
    print(f"Pearson Correlation:  {p_corr:.4f} (p-value: {p_val:.4e})")
    print(f"Spearman Correlation: {s_corr:.4f} (p-value: {s_val:.4e})")
    print(f"Cohen's Kappa:        {kappa:.4f}")


if __name__ == "__main__":
    check_and_calculate_agreement()
