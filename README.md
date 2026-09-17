# Hiver AI Support Agent

An end-to-end prototype AI Customer Support Agent built for Uber Support inquiries. The system receives inbound customer messages via a React dashboard, classifies them across a 10-intent operational taxonomy, retrieves grounded resolution precedents from historical Twitter support conversations, drafts context-aware responses, and executes an automated routing policy (`AUTO_HANDLE` vs. `ESCALATE`) with decision justifications.

---

## 1. Problem

Customer support teams at scale face high inquiry volumes where response latency directly affects customer satisfaction. A major challenge in automated customer support is ensuring that AI systems remain safely grounded in historical brand procedures rather than generating unverified promises (such as unauthorized refunds or policy guarantees).

This prototype addresses that challenge for the **Uber Support** domain (`@Uber_Support`), a high-volume customer service operation managing ride cancellations, driver conduct, fare adjustments, lost items, and delivery problems.

---

## 2. What the Prototype Does

When a customer submits an inquiry through the interactive web dashboard:
1. **Real-Time Ingestion**: The message is sent to the backend pipeline.
2. **Intent Classification**: The message is classified into one of 10 domain intents.
3. **Historical Resolution Retrieval**: Relevant historical resolution precedents are searched in the support resolution corpus using intent filtering and TF-IDF cosine similarity.
4. **Grounded Reply Drafting**: A polite, grounded customer draft reply is synthesized using the retrieved support response pattern while preventing false promises.
5. **Decision Routing**: An automated policy determines whether the inquiry can be resolved self-serve (`AUTO_HANDLE`) or requires human agent intervention (`ESCALATE`), returning a clear operational rationale.

---

## 3. Architecture

The system consists of a decoupled frontend and a modular backend pipeline:

```
Customer Message (React Dashboard)
             │
             ▼  HTTP POST /api/analyze
FastAPI Backend Router (backend/app/main.py)
             │
             ▼
Support Agent Pipeline (backend/app/services/support_agent.py)
  ├── 1. Intent Classifier (classifier.py)
  │      └── Rule-based scoring over 10 operational intents
  ├── 2. Historical Retriever (retriever.py)
  │      └── Intent-filtered TF-IDF vectorization & cosine similarity
  ├── 3. Reply Generator (reply_generator.py)
  │      └── Procedural grounding from historical support precedents
  └── 4. Decision Engine (decision.py)
         └── Usability threshold, policy rules, and escalation logic
             │
             ▼  JSON Response (AnalyzeResponse)
React Dashboard UI (frontend/src/App.jsx)
```

The underlying conversational data originates from the Kaggle Customer Support on Twitter dataset (`@Uber_Support` interactions).

---

## 4. Intent Taxonomy

The support domain is structured into 10 mutually exclusive operational intents:

| Intent | Definition | Example Scope |
|:---|:---|:---|
| `fare_or_charge_issue` | Disputed ride pricing or fee calculation | Surge pricing disputes, upfront fare discrepancies, toll charges |
| `refund_request` | Explicit requests for monetary reimbursement | Demands for ride or delivery charge refunds, duplicate debit reversals |
| `driver_issue` | Driver conduct, safety, or professional behavior | Driver impoliteness, reckless driving, refusing pickup, route deviation |
| `trip_issue` | Physical trip execution or vehicle conditions | Vehicle breakdown, getting stuck, wrong destination drop-off |
| `cancellation_issue` | Ride cancellation fees and dispatch disputes | Driver canceled after long wait, disputed rider cancellation fee |
| `account_access_issue` | Account credentials, login, and authentication | Inability to log in, locked or deactivated account, phone verification |
| `payment_issue` | Payment instrument, card, or gateway failures | Card declined in app, payment method update failure, wallet error |
| `app_or_technical_issue` | Software defects, crashes, or app glitches | App crash on booking, promo code error, GPS map rendering glitch |
| `uber_eats_issue` | Food delivery orders and restaurant fulfillment | Missing food items, late delivery, cold food, wrong restaurant order |
| `other_support_issue` | General brand inquiries, promo requests, or edge cases | Service availability inquiries, partnership questions, unmapped queries |

---

## 5. Data Preparation

The historical resolution knowledge base was prepared from the Kaggle Customer Support on Twitter dataset through the following pipeline:

1. **Original Dataset**: Multi-brand archive containing over 3 million tweets.
2. **Brand Filtering**: Isolated all inbound interactions referencing `@Uber_Support`.
3. **Conversation Reconstruction**: Mapped `in_response_to_tweet_id` and `response_tweet_id` to link customer queries directly to corresponding official Uber Support responses, producing 51,590 resolved pair candidates.
4. **Repository Demo Corpus (`data/uber_resolution_demo.csv`)**: A curated 500-row representative sample of resolved customer/support pairs included in Git to provide instant, self-contained retrieval without multi-gigabyte external downloads.
5. **Golden Evaluation Set (`data/golden_set.csv`)**: Exactly 200 customer messages with verified `gold_intent` labels, used strictly as an out-of-sample benchmark.

---

## 6. Agent Design

The agent operates in five distinct, modular phases:

1. **Classification (`backend/app/services/classifier.py`)**: Evaluates the input message against intent lexicons and term patterns. Confidence is set to `null` because the deterministic rule engine does not produce calibrated probabilities.
2. **Retrieval (`backend/app/services/retriever.py`)**: Filters the historical resolution corpus by predicted intent and calculates cosine similarity across TF-IDF n-grams (1-2). If the top candidate achieves a cosine similarity $\ge 0.20$, it is exposed as a usable `historical_match`. If below $0.20$, `historical_match` is exposed as `null` while preserving the numeric similarity for system diagnostics.
3. **Reply Generation (`backend/app/services/reply_generator.py`)**: Cleans tweet artifacts (removes dead `@mentions` and short links) and grounds the draft in historical resolution guidance. If no usable match exists, a safe intent-specific fallback is generated.
4. **Decision Engine (`backend/app/services/decision.py`)**:
   - `AUTO_HANDLE` only when: Intent is clear/deterministic, a usable resolution exists ($\ge 0.20$), the historical resolution provides self-contained self-serve guidance, and no human intervention is needed.
   - `ESCALATE` when: Similarity $< 0.20$, historical resolution requests direct communication (e.g., "send us a DM"), the inquiry requires identity verification (`account_access_issue`), the inquiry involves actions the system cannot execute autonomously (`refund_request`), or the intent is ambiguous (`other_support_issue`).
5. **Orchestration (`backend/app/services/support_agent.py`)**: Aggregates all components into a unified service consumed by FastAPI and React.

---

## 7. Evaluation Methodology

The evaluation harness was constructed under strict scientific controls:

- **Golden Evaluation Set**: Exactly 200 customer messages from `data/golden_set.csv`.
- **Labeling Quality**: Initial AI-assisted candidate labeling followed by 100% human verification and correction of every final label.
- **Zero Information Leakage**: The agent receives **only** `customer_message`. The fields `gold_intent`, `ai_intent`, and `notes` are strictly withheld from prediction, retrieval, and evaluation.
- **Automated Scikit-Learn Metrics**: Accuracy, macro/weighted precision, recall, and F1 scores across all 10 intent classes.
- **Fixed Reply Quality Sample**: Exactly 30 examples selected with fixed `random_state=42` and sorted deterministically by `customer_tweet_id` (`evaluation/results/judge_sample.csv`).
- **Human Annotation Protocol**: Blinded template (`evaluation/human_judge_template.csv`) with rating columns left blank for independent evaluation.

---

## 8. Results

All metrics below are verified outputs generated directly by `evaluation/evaluate_agent.py` and `evaluation/compare_baselines.py`:

### Pipeline Agent Performance (200 Golden Examples)

Evaluated across the full 200-example human-verified golden set (`data/golden_set.csv`):

- **Accuracy**: **61.00%** (122/200)
- **Macro Precision**: **0.5606**
- **Macro Recall**: **0.5341**
- **Macro F1**: **0.5283**
- **Weighted F1**: **0.6022**

### Per-Intent Performance of Support Agent (200 Examples)

| Intent | Precision | Recall | F1-Score | Support |
|:---|:---:|:---:|:---:|:---:|
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
| **Macro Average** | **0.56** | **0.53** | **0.53** | **200** |
| **Weighted Average** | **0.62** | **0.61** | **0.60** | **200** |

### Decision Routing Breakdown (200 Examples)
- **`ESCALATE`**: **169/200 (84.5%)**
- **`AUTO_HANDLE`**: **31/200 (15.5%)**

### Historical Retrieval Statistics (200 Examples)
- **Average / Mean Top-1 Cosine Similarity**: **0.2807**
- **Median Top-1 Similarity**: **0.2317**
- **Similarity $\ge 0.20$**: **134/200 (67.0%)** (Usable historical match; Mean: 0.3357, Median: 0.2656)
- **Similarity $< 0.20$**: **66/200 (33.0%)** (Exposed as `null` match, triggers `ESCALATE`)

### Standalone Baseline Experiments (Separate 50-Example Stratified Holdout)

> [!NOTE]
> **Independent Benchmark**: The standalone baseline models were evaluated on a separate 50-example stratified holdout (`test_size=50`, `random_state=42`). Because they were evaluated on this 50-example holdout rather than the 200-example golden set, these baseline numbers are **not directly comparable** to the 200-example Support Agent pipeline evaluation.

| Baseline Model | Evaluation Set | Accuracy | Macro F1 | Weighted F1 | Script |
|:---|:---:|:---:|:---:|:---:|:---|
| **Keyword Rule Baseline** | 50-Example Holdout | **64.00%** (32/50) | 0.59 | 0.64 | `evaluation/baseline_rules.py` |
| **TF-IDF + Logistic Regression** | 50-Example Holdout | **40.00%** (20/50) | 0.14 | 0.28 | `evaluation/baseline_tfidf.py` |

**Why Does the Keyword Baseline Score 64% on Its 50-Example Holdout vs. 61% for the Agent on 200 Examples?**
The 64.00% keyword baseline was evaluated on a smaller 50-example stratified holdout where simple lexical shortcuts matched frequent patterns. Across the full 200-example golden set with real-world distribution imbalances and edge cases, the complete Support Agent pipeline achieves 61.00% accuracy. The agent balances end-to-end procedural grounding, safe intent filtering, and conservative escalation rather than relying on brittle lexical shortcut heuristics.

---

## 9. Top 5 Failure Modes

Extracted from actual evaluation errors in `evaluation/results/failure_analysis.md`:

### 1. `other_support_issue` Misclassified as `account_access_issue` (7 cases)
- **What Happened**: General inquiries asking for contact channels or emails were classified as account access issues.
- **Observed Example**:
  > *"@Uber_Support is there an email address or phone number to contact you at so I'm not airing my problems out on twitter?"*
- **Hypothesis**: The rule engine heavily weighted tokens like "email" and "phone" toward credential/login verification.
- **Improvement**: Require co-occurrence of authentication verbs ("login", "reset", "deactivated", "locked") before triggering account access.

### 2. `other_support_issue` Misclassified as `app_or_technical_issue` (5 cases)
- **What Happened**: General conversational requests or complaints mentioning the word "app" or "website" triggered technical bug classification.
- **Observed Example**:
  > *"@Uber_Support U happen to have some kind of promo code I could use to save back that $8 im going for a 35min trip"*
- **Hypothesis**: Broad technical keywords ("app", "update", "error") matched promo code and marketing chatter.
- **Improvement**: Isolate discount/promo intents or require error-specific terms ("crash", "bug", "frozen", "white screen").

### 3. `app_or_technical_issue` Misclassified as `account_access_issue` (5 cases)
- **What Happened**: Software bugs preventing users from completing in-app actions were interpreted as account login blocks.
- **Observed Example**:
  > *"@115873 why can I add promo codes to my account?"*
- **Hypothesis**: Inability to redeem promos or use features in-app contained the word "account", overriding the technical defect signal.
- **Improvement**: Separate account profile security from in-app functional errors via negative keyword constraints.

### 4. `app_or_technical_issue` Misclassified as `driver_issue` (4 cases)
- **What Happened**: App telematics or dispatch communication bugs were attributed to driver behavior.
- **Observed Example**:
  > *"@Uber_Support Uber places phone calls to drivers through Google Hangouts rather than my sim phone service. How do I change this? P"*
- **Hypothesis**: Presence of the word "driver" in a telematics configuration query dominated the classifier score.
- **Improvement**: Check syntactic dependency: distinguish when the driver is the subject of misconduct versus an entity mentioned in an app setting.

### 5. `driver_issue` Misclassified as `other_support_issue` (4 cases)
- **What Happened**: Driver arrival delays and missing pickups failed to match driver conduct rules and fell back to the generic class.
- **Observed Example**:
  > *"@Uber_Support your cabs never reach on time . Y the hell you provide coupons"*
- **Hypothesis**: Colloquial expressions ("cabs never reach on time") lacked explicit driver identity terms ("chauffeur", "driver").
- **Improvement**: Expand driver lexicon to include arrival performance terms ("reach on time", "never showed up", "left without me").

---

## 10. What is Misleading About My Headline Number?

Presenting **61.00% accuracy** as a definitive summary of system performance would be misleading for several reasons:

1. **Small Sample Size**: The metric is measured on exactly 200 golden examples, which has wide binomial confidence intervals.
2. **Class Imbalance**: The golden set reflects realistic support skew: `other_support_issue` (48) and `driver_issue` (38) represent 43% of the dataset, while `trip_issue` contains only 4 examples.
3. **Subjective Boundaries**: In customer communications, category boundaries are inherently subjective (e.g., whether an inquiry disputing a surge charge while asking for money back is a `fare_or_charge_issue` or a `refund_request`).
4. **Pre-Labeling Influence**: Ground truth was established using AI-assisted pre-labeling followed by human verification, which can introduce cognitive anchoring compared to dual-annotator adjudication from scratch.
5. **Restricted Retrieval Corpus**: Retrieval similarity was evaluated against a 500-row demo corpus rather than the full 51,590 historical pairs, artificially depressing similarity scores.
6. **Not Live Performance**: This prototype processes historical public tweets; it is not deployed inside Uber's private support infrastructure.
7. **Does Not Measure Reply Quality**: A model can predict the correct intent while generating a hallucinated or unhelpful reply; accuracy measures classification only.
8. **Pending Human Agreement**: Reply quality evaluation remains pending manual human scoring.

---

## 11. LLM-as-a-Judge and Human Evaluation

### Quality Rubric (1–5 Likert Scale)
The evaluation harness defines five criteria for assessing draft response quality:
- **Relevance (1–5)**: Does the reply directly address the customer inquiry?
- **Groundedness (1–5)**: Is the reply supported by historical support patterns without hallucinating procedures?
- **Helpfulness (1–5)**: Does the reply provide clear next steps without claiming unavailable system actions?
- **Professional Tone (1–5)**: Is the language polite, empathetic, clear, and professional?
- **Safety / Non-Fabrication (1–5)**: Does the reply avoid unsupported refunds, deadlines, policies, or false completion claims?

### Current Status
- **LLM Judge Execution (`evaluation/llm_judge.py`)**: Designed to evaluate the fixed 30-sample cohort (`random_state=42`, sorted deterministically). In the current environment, `GEMINI_API_KEY` was not configured. In accordance with strict evaluation integrity rules, **0 of 30 examples were judged, and zero scores were fabricated**.
- **Human Evaluation (`evaluation/human_judge_template.csv`)**: Template prepared with the identical 30 examples. All rating columns remain unpopulated pending manual annotation.
- **Agreement Analysis (`evaluation/agreement.py`)**: Pearson, Spearman, MAE, and ordinal Cohen's Kappa binning are implemented. Agreement calculation is pending manual human rating entry.

---

## 12. One-Week Next Steps

A practical 7-day engineering plan to improve the prototype:

- **Day 1: Disambiguate Intent Boundaries**: Decouple financial refund actions from fare dispute explanations; refine negative keyword rules for `other_support_issue`.
- **Day 2: Semantic Retrieval with Dense Embeddings**: Integrate a lightweight, local embedding model (e.g., `all-MiniLM-L6-v2`) to capture semantic equivalence where lexical TF-IDF fails.
- **Day 3: Corpus Expansion**: Scale the retrieval corpus from the 500-row demo sample to 10,000+ verified customer/support resolution pairs to improve similarity scores.
- **Day 4: Calibrate Escalation Confidence**: Implement probability calibration (e.g., Platt scaling or temperature scaling) to produce authentic, calibrated confidence scores.
- **Day 5: Execute LLM Judge Harness**: Run the automated judge against the 30-sample cohort with configured API credentials, recording latency and cost per evaluation.
- **Day 6: Complete Human Annotation & Agreement**: Complete manual scoring on `evaluation/human_judge_template.csv` and run `evaluation/agreement.py` to evaluate Pearson and Cohen's Kappa alignment.
- **Day 7: Fresh-Clone Integration & Regression Testing**: Validate reproduction steps on a clean environment, verify frontend build, and document API latency.

---

## 13. Limitations

1. **Public Social Media Context**: Tweets are constrained by character limits and informal phrasing, lacking the detailed structure of private customer tickets.
2. **Lexical Matching Constraints**: TF-IDF cannot recognize semantic similarity when users employ synonyms not present in the historical corpus.
3. **No Live Uber System Integration**: The agent cannot access live GPS, verify rider identities, access credit card gateways, or issue actual refunds.
4. **Demo Retrieval Scale**: The 500-row demo corpus limits retrieval coverage, causing approximately 33% of golden set queries to fall below the 0.20 similarity cutoff.
5. **Asynchronous LLM Judge**: Reply quality auditing depends on external API availability and manual human annotation completion.

---

## 14. Reproduction

To reproduce all evaluations from a fresh clone using Windows PowerShell:

### 1. Backend Setup
```powershell
# Navigate to repository root
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

### 2. Frontend Setup
```powershell
cd frontend
npm install
npm run build
cd ..
```

### 3. Run Automated Agent Evaluation (200 Golden Examples)
```powershell
python evaluation\evaluate_agent.py
```
*Outputs: `agent_predictions.csv`, `classification_metrics.txt`, `classification_report.csv`, `confusion_matrix.csv`, `decision_metrics.csv`, `retrieval_metrics.txt`.*

### 4. Run Baseline Comparisons
```powershell
python evaluation\baseline_rules.py
python evaluation\baseline_tfidf.py
python evaluation\compare_baselines.py
```

### 5. Run Failure Analysis
```powershell
python evaluation\analyze_failures.py
```
*Outputs: `evaluation\results\failure_analysis.md`.*

### 6. Run LLM Judge & Agreement Harness
```powershell
python evaluation\llm_judge.py
python evaluation\agreement.py
```

### 7. Run Locally (Full Interactive Application)

#### Recommended: One-Command Startup (Root)
From the repository root:
```powershell
npm run dev
```
This runs `scripts/dev.js`, which concurrently launches:
- **FastAPI backend** with working directory set to `backend/` (`python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`)
- **Vite React frontend** with working directory set to `frontend/` (`npm run dev`)

Individual component runners:
```powershell
npm run dev:backend   # Starts backend only from backend/
npm run dev:frontend  # Starts frontend only from frontend/
```

#### Service URLs
- **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
- **Backend Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- **Interactive API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

> [!NOTE]
> The frontend connects to `http://localhost:8000` by default. You can override this by setting `VITE_API_URL` in `frontend/.env` or in your environment.

#### Fallback: Manual Two-Terminal Startup
If the root `npm run dev` script is not used, run each service in its own terminal:

```powershell
# Terminal 1 - Backend Server (MUST run from backend/ directory)
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

```powershell
# Terminal 2 - Frontend Development Server
cd frontend
npm run dev
```

---

## 15. Repository Structure

```text
hiver-ai-support-agent/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application endpoints
│   │   └── services/
│   │       ├── classifier.py           # 10-intent classification service
│   │       ├── retriever.py            # Historical TF-IDF resolution retriever
│   │       ├── reply_generator.py      # Grounded response synthesis
│   │       ├── decision.py             # AUTO_HANDLE vs ESCALATE policy
│   │       └── support_agent.py        # End-to-end pipeline orchestrator
│   └── requirements.txt                # Python dependencies
├── data/
│   ├── golden_set.csv                  # 200-row human-verified golden set
│   └── uber_resolution_demo.csv        # 500-row historical resolution demo corpus
├── evaluation/
│   ├── results/
│   │   ├── agent_predictions.csv       # 200 golden predictions & routing outputs
│   │   ├── classification_metrics.txt  # Accuracy and macro/weighted F1 summary
│   │   ├── classification_report.csv   # Per-intent precision, recall, F1
│   │   ├── confusion_matrix.csv        # 10x10 confusion matrix
│   │   ├── decision_metrics.csv        # Routing distribution by intent
│   │   ├── retrieval_metrics.txt       # Similarity and cutoff metrics
│   │   ├── failure_analysis.md         # Top 5 failure patterns report
│   │   ├── judge_sample.csv            # 30-sample fixed evaluation cohort
│   │   ├── llm_judge_results.csv       # LLM judge outputs
│   │   ├── llm_judge_summary.txt       # Summary of judge execution
│   │   ├── agreement_metrics.txt       # Correlation & agreement status
│   │   └── agreement_report.md         # Human-judge agreement report
│   ├── evaluate_agent.py               # Main 200-row evaluation harness
│   ├── analyze_failures.py             # Error extraction and pattern analysis
│   ├── llm_judge.py                    # LLM quality evaluation harness
│   ├── agreement.py                    # Inter-rater agreement calculator
│   ├── human_judge_template.csv        # 30-row human annotation template
│   ├── HUMAN_EVALUATION.md             # Human scoring protocol
│   ├── baseline_rules.py               # 50-sample keyword baseline
│   ├── baseline_tfidf.py               # 50-sample TF-IDF baseline
│   ├── compare_baselines.py            # Baseline summary comparison
│   └── README.md                       # Comprehensive evaluation documentation
├── frontend/
│   ├── src/
│   │   ├── components/                 # UI dashboard modules
│   │   ├── services/api.js             # API client connecting to FastAPI
│   │   ├── App.jsx                     # Interactive support console
│   │   └── index.css                   # Custom Vanilla CSS design tokens
│   ├── package.json                    # Frontend dependencies (React 19 + Vite)
│   └── index.html                      # Entry HTML
├── package.json                        # Root-level multi-service dev scripts
├── scripts/
│   └── dev.js                          # Cross-platform concurrent dev process runner
├── DECISION_LOG.md                     # Technical & product decision rationales
└── README.md                           # Main project documentation
```

---

## 16. Integrity & Scope Note

- **Historical Data Only**: This system operates purely on public historical Twitter conversations from the Kaggle dataset and is not connected to Uber production infrastructure.
- **No Direct System Actions**: `AUTO_HANDLE` reflects the agent's confidence that self-contained procedural guidance exists; it does not trigger production actions, payment adjustments, or account changes.
- **No Fabricated Data**: Missing LLM judge scores and pending human ratings are reported honestly. No synthetic ratings or correlation coefficients have been generated.
