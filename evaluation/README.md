# Hiver AI Support Agent — Comprehensive Evaluation Report

This document details the reproducible evaluation protocol, baseline comparisons, agent performance metrics, failure analysis, routing decision dynamics, and human-judge agreement framework on the **200-example human-verified golden dataset**.

---

## 1. Dataset & Ground-Truth Methodology

- **Source Corpus**: Kaggle Customer Support on Twitter (`@Uber_Support`).
- **Golden Evaluation Set**: `data/golden_set.csv` containing **200 customer messages** annotated across the 10-intent taxonomy.
- **Labeling Quality**: Initial AI-assisted candidate labeling followed by rigorous human verification to eliminate label noise. All 200 rows have verified `gold_intent` labels.
- **Strict Information Isolation**: During all evaluations, **zero label leakage** occurs. The agent only receives `customer_message` (`text`). The fields `gold_intent`, `ai_intent`, and `notes` are strictly isolated from the classification, retrieval, and decision engines.

---

## 2. Intent Taxonomy (10 Classes)

| Intent | Golden Set Distribution |
|---|---:|
| `other_support_issue` | 48 |
| `driver_issue` | 38 |
| `account_access_issue` | 24 |
| `uber_eats_issue` | 22 |
| `fare_or_charge_issue` | 15 |
| `app_or_technical_issue` | 15 |
| `cancellation_issue` | 14 |
| `refund_request` | 12 |
| `payment_issue` | 8 |
| `trip_issue` | 4 |
| **Total** | **200** |

---

## 3. Baseline Evaluations (50-Sample Holdout)

Two standalone baseline models were previously evaluated on a 25% stratified holdout (50 samples, `random_state=42`):

1. **TF-IDF + Logistic Regression Baseline**:
   - Accuracy: **`40.00%`**
   - Weighted F1: **`0.28`**
   - Script: `evaluation/baseline_tfidf.py`
2. **Keyword Rule-Based Baseline**:
   - Accuracy: **`64.00%`**
   - Macro F1: **`0.59`**
   - Weighted F1: **`0.64`**
   - Script: `evaluation/baseline_rules.py`

*Note on 64% vs Full Agent*: The 64% headline number is measured on the 50-example stratified holdout. Below, we report the end-to-end support-agent pipeline evaluated on the entire **200-example golden set**.

---

## 4. Full AI Support Agent Evaluation (200 Examples)

Executed via:
```bash
python evaluation/evaluate_agent.py
```

### Overall Classification Metrics
- **Evaluated Inquiries**: 200
- **Accuracy**: **`61.00%`** (122 / 200 correct)
- **Macro Precision**: **`0.5606`**
- **Macro Recall**: **`0.5341`**
- **Macro F1**: **`0.5283`**
- **Weighted F1**: **`0.6022`**

### Per-Intent Classification Breakdown

| Intent | Precision | Recall | F1-Score | Support |
|---|---:|---:|---:|---:|
| `account_access_issue` | 0.52 | 0.67 | 0.58 | 24 |
| `app_or_technical_issue` | 0.29 | 0.27 | 0.28 | 15 |
| `cancellation_issue` | 0.67 | 0.57 | 0.62 | 14 |
| `driver_issue` | 0.71 | 0.79 | 0.75 | 38 |
| `fare_or_charge_issue` | 0.33 | 0.20 | 0.25 | 15 |
| `other_support_issue` | 0.69 | 0.65 | 0.67 | 48 |
| `payment_issue` | 0.38 | 0.38 | 0.38 | 8 |
| `refund_request` | 1.00 | 0.42 | 0.59 | 12 |
| `trip_issue` | 0.29 | 0.50 | 0.36 | 4 |
| `uber_eats_issue` | 0.74 | 0.91 | 0.82 | 22 |
| **Micro Avg / Accuracy** | **0.61** | **0.61** | **0.61** | **200** |
| **Macro Average** | **0.56** | **0.53** | **0.53** | **200** |
| **Weighted Average** | **0.62** | **0.61** | **0.60** | **200** |

*Artifacts*:
- Saved predictions: `evaluation/results/agent_predictions.csv`
- Classification report: `evaluation/results/classification_report.csv`
- Classification metrics: `evaluation/results/classification_metrics.txt`
- Confusion matrix: `evaluation/results/confusion_matrix.csv`

---

## 5. Routing Decision Distribution & Policy

The agent evaluates incoming inquiries using the grounded decision policy:

- **`ESCALATE`**: **169 inquiries (84.50%)**
- **`AUTO_HANDLE`**: **31 inquiries (15.50%)**

### Decision Policy Rules:
- **`AUTO_HANDLE`** only when:
  - Predicted intent is deterministic and clear (excludes ambiguous fallback `other_support_issue`)
  - A usable historical resolution exists (`historical_match != null`)
  - Cosine similarity $\ge 0.20$
  - Historical support response provides self-contained resolution guidance
  - No direct human intervention is required
- **`ESCALATE`** when:
  - Cosine similarity $< 0.20$ (retrieval match below threshold)
  - No usable historical resolution exists (`historical_match == null`)
  - Historical support response requests direct communication ("send us a DM", "contact us", "send us a note")
  - Issue requires identity verification or account-level action (`account_access_issue`)
  - Issue is ambiguous (`other_support_issue`) or requires actions the system cannot autonomously perform (`refund_request` financial disbursement)

> [!NOTE]
> Classifier confidence intentionally remains `null` because the deterministic intent classifier does not emit uncalibrated statistical probabilities. `AUTO_HANDLE` never depends on a fabricated confidence score.

*Artifact*: `evaluation/results/decision_metrics.csv`

---

## 6. Historical Resolution Retrieval Analysis

The evaluation distinguishes nearest candidate discovery from usable historical resolution matches:

- **Total Inquiries Evaluated**: 200
- **1. Nearest Candidates Discovered**: **200 (100.00%)**
  - Mean Similarity (all candidates): **`0.2807`**
  - Median Similarity (all candidates): **`0.2317`**
- **2. Usable Historical Matches ($\ge 0.20$)**: **134 (67.00%)**
  - Mean Similarity (usable matches): **`0.3357`**
  - Median Similarity (usable matches): **`0.2656`**
- **3. Below-Threshold Retrieval ($< 0.20$)**: **66 (33.00%)**
  - Excluded from `historical_match` (exposed as `null`)
  - Correctly triggers the `ESCALATE` routing policy
- **4. Zero Similarity / No Candidate ($\le 0.0$)**: **0 (0.00%)**

*Artifact*: `evaluation/results/retrieval_metrics.txt`


---

## 7. Failure Analysis (Top 5 Patterns)

Executed via:
```bash
python evaluation/analyze_failures.py
```
Total misclassifications: 78 / 200 (39.00% error rate).

### Top Failure Patterns Observed:
1. **`other_support_issue` $\to$ `account_access_issue` (7 cases)**:
   Inquiries mentioning phrases like "email", "sign in", or "phone" in general context trigger account access rules.
2. **`other_support_issue` $\to$ `app_or_technical_issue` (5 cases)**:
   General complaints mentioning "website", "link", or "app" trigger technical issue rules.
3. **`app_or_technical_issue` $\to$ `account_access_issue` (5 cases)**:
   Inability to log in due to an app crash is classified as account access rather than a technical software defect.
4. **`app_or_technical_issue` $\to$ `driver_issue` (4 cases)**:
   Customer messages describing driver app glitches or pickup navigation bugs trigger driver keywords.
5. **`driver_issue` $\to$ `other_support_issue` (4 cases)**:
   Unconventional phrasing of driver complaints lacking explicit driver keywords falls back to the generic class.

*Artifact*: `evaluation/results/failure_analysis.md`

---

## 8. LLM-as-Judge & Human Agreement Framework

### LLM Judge (`evaluation/llm_judge.py`)
- Evaluates draft reply quality on 5 dimensions (1–5 scale): *Relevance*, *Groundedness*, *Helpfulness*, *Professional Tone*, and *Safety*.
- Samples a fixed subset of 30 examples (`random_state=42`).
- **API Status**: When `GEMINI_API_KEY` is not present or exhausted by quota limits, the script logs the limitation honestly and leaves records unjudged rather than fabricating artificial scores.

### Human Annotation (`evaluation/human_judge_template.csv` & `evaluation/HUMAN_EVALUATION.md`)
- Prepared template containing the exact same 30-sample slice.
- Human rating columns are left unpopulated for authentic independent annotation.
- `evaluation/agreement.py` evaluates Pearson, Spearman, and Cohen's Kappa correlations once ratings are provided.
