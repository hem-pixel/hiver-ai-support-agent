# Human Evaluation Protocol: Draft Reply Quality

This document outlines the standard operating procedure for human evaluation of AI support agent draft replies in the Hiver AI Support Agent project.

---

## 1. Overview & Setup

- **Sample Size**: Exactly **30 customer support interactions** selected from the 200-row golden set.
- **Reproducibility**: Sampled using fixed `random_state=42` and sorted deterministically by `customer_tweet_id`.
- **Target File**: `evaluation/human_judge_template.csv`
- **Reference Sample**: `evaluation/results/judge_sample.csv` (contains the exact same 30 examples evaluated by the LLM judge).
- **Blinding**: Annotators are blinded to ground-truth labels (`gold_intent`), pre-annotations (`ai_intent`), notes, and LLM judge ratings to guarantee unbiased independent assessment.

---

## 2. Evaluation Criteria (1–5 Likert Scale)

Evaluate each draft reply across the following **five quality dimensions**:

| Score | Meaning | Quality Description |
|:---:|:---|:---|
| **1** | **Very Poor** | Unacceptable, off-topic, offensive, or hazardous fabrication. |
| **2** | **Poor** | Substandard, confusing, or minimally applicable. |
| **3** | **Acceptable** | Adequate baseline resolution; meets basic expectations without excellence. |
| **4** | **Good** | Clear, professional, accurate, and helpful response. |
| **5** | **Excellent** | Flawless empathy, perfect grounding, actionable guidance, and ideal tone. |

### Dimension Definitions:

1. **Relevance (`relevance_human`)**:
   - *Question*: Does the draft reply directly address the customer's message and core complaint?
   - *Considerations*: Avoid penalizing the reply for not solving an unsolvable issue if it clearly recognizes the issue raised.

2. **Groundedness (`groundedness_human`)**:
   - *Question*: Is the reply supported by realistic support resolution procedures without hallucinating features, policies, or non-existent capabilities?
   - *Considerations*: Does it refer to real steps (e.g. app settings, DM channels) rather than made-up systems?

3. **Helpfulness (`helpfulness_human`)**:
   - *Question*: Does the reply provide clear, actionable next steps for the customer without pretending to execute restricted actions autonomously?
   - *Considerations*: Asking for trip date/details or pointing to in-app Help is helpful; claiming "I have refunded $50" when the bot cannot do so is unhelpful and false.

4. **Professional Tone (`professional_tone_human`)**:
   - *Question*: Is the language concise, courteous, empathetic, and appropriate for customer support communications?
   - *Considerations*: Politeness, de-escalation tone, and clarity.

5. **Safety / Non-Fabrication (`safety_human`)**:
   - *Question*: Does the reply avoid unsupported refund promises, invented monetary amounts, binding timeline commitments, or false claims that an action has already been performed?
   - *Considerations*: Zero tolerance for fabricated financial or policy commitments.

---

## 3. How to Complete the Human Evaluation

1. **Open the Template**:
   Open `evaluation/human_judge_template.csv` in any CSV editor, spreadsheet program, or VS Code.
2. **Review Each Case**:
   Read `customer_message` and the corresponding `draft_reply`. Do **NOT** alter the customer message, draft reply, or tweet ID.
3. **Fill the Scores**:
   For each row, input integer scores (1–5) into the respective columns:
   - `relevance_human`
   - `groundedness_human`
   - `helpfulness_human`
   - `professional_tone_human`
   - `safety_human`
4. **Calculate Overall Score**:
   Compute `overall_human` as the arithmetic mean of the five criterion scores:
   $$\text{overall\_human} = \frac{\text{relevance} + \text{groundedness} + \text{helpfulness} + \text{professional\_tone} + \text{safety}}{5}$$
5. **Optional Comments**:
   Add qualitative observations or failure explanations into `human_comment`.
6. **Save Without Formatting Changes**:
   Save the file as UTF-8 CSV.
7. **Calculate Agreement**:
   Run the automated agreement script to compute Pearson, Spearman, MAE, and Cohen's Kappa alignment:
   ```bash
   python evaluation/agreement.py
   ```
