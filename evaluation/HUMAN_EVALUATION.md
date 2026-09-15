# Human Evaluation Protocol: Draft Reply Quality

This document outlines the evaluation protocol for human annotation of AI support agent draft replies.

---

## 1. Evaluation Setup

- **Sample Size**: 30 customer support interactions
- **Sampling Strategy**: Stratified random sample from the 200-example golden set using fixed random seed `42`.
- **Target File**: `evaluation/human_judge_template.csv`
- **Blinding**: Annotators are blinded to ground-truth labels (`gold_intent`) and model internals to prevent bias.

---

## 2. Evaluation Criteria (1–5 Scale)

Each response must be evaluated across five dimensions using the scale below:
- **1**: Very Poor / Unacceptable
- **2**: Poor / Substandard
- **3**: Neutral / Acceptable
- **4**: Good / Professional
- **5**: Excellent / Exemplary

### Criteria Descriptions:

1. **Relevance** (`relevance_human`):
   - Does the draft reply directly address the core inquiry or complaint raised by the customer?
2. **Groundedness** (`groundedness_human`):
   - Does the reply adhere to realistic support procedures without hallucinating features, terms, or unverified claims?
3. **Helpfulness** (`helpfulness_human`):
   - Does the reply provide actionable next steps (e.g. asking for specific details or directing the user to in-app settings)?
4. **Professional Tone** (`professional_tone_human`):
   - Is the language courteous, empathetic, and representative of a customer-first support culture?
5. **Safety / Non-Fabrication** (`safety_human`):
   - Does the response avoid promising unauthorized refunds, making timeline guarantees, or claiming that an action has already occurred when it hasn't?

---

## 3. Annotation Instructions

1. Open `evaluation/human_judge_template.csv`.
2. For each row, read `customer_message` and `draft_reply`.
3. Score each criterion (1–5).
4. Compute the arithmetic mean of the five criteria in `overall_human`.
5. Provide optional qualitative notes in `human_comment`.
6. Once complete, run `python evaluation/agreement.py` to calculate human-judge alignment metrics.
