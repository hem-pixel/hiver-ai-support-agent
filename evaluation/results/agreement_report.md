# LLM Judge & Human Annotator Agreement Report

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
