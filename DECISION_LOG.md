# Engineering & Product Decision Log

This document records the rationale, architectural considerations, and trade-offs for 15 key technical and product decisions made during the design and development of the Hiver AI Support Agent prototype.

---

### Decision 1: Focus on Uber Support within Kaggle Customer Support on Twitter
- **Decision**: Select `@Uber_Support` inbound customer interactions from the Kaggle Customer Support on Twitter dataset as the evaluation domain.
- **Why**: Uber support interactions feature rich, multi-turn conversational data covering high-volume operational customer service challenges: ride cancellations, driver misconduct, pricing/fare disputes, refunds, and food deliveries.
- **Trade-off / Downside**: Twitter customer inquiries are constrained by character limits, often containing informal slang, shorthand, missing context, and public frustration, which introduces higher linguistic noise than structured email tickets.

---

### Decision 2: Choose a Small, Cohesive 10-Intent Taxonomy
- **Decision**: Restrict classification to 10 mutually exclusive, high-level operational intents rather than a granular 50+ category hierarchy.
- **Why**: A focused taxonomy provides stable routing semantics for a support agent. It enables clear mapping from customer problem types to safe resolution actions (self-serve vs. human triage).
- **Trade-off / Downside**: Granular nuances within broad categories (such as grouping VoIP app calling issues under `app_or_technical_issue`) can lead to category overlap and boundary ambiguity.

---

### Decision 3: Separate `refund_request` from `fare_or_charge_issue`
- **Decision**: Treat explicit refund requests (`refund_request`) as an autonomous intent separate from billing/fare calculation inquiries (`fare_or_charge_issue`).
- **Why**: An inquiry disputing a surge multiplier or route calculation requires explanation and route review, whereas a refund request demands immediate financial disbursement authorization. Decoupling them allows dedicated financial safety controls.
- **Trade-off / Downside**: In customer service messages, users frequently bundle both in a single sentence ("You overcharged me on surge, give me my refund!"), causing keyword overlap and classification friction.

---

### Decision 4: Introduce `other_support_issue` as an Explicit Fallback Class
- **Decision**: Maintain `other_support_issue` as a formal class in the taxonomy rather than forcing ambiguous messages into rider/driver buckets.
- **Why**: Real-world inbound queues receive general brand chatter, marketing queries, promos, and edge cases. Having an explicit unmapped class prevents false confidence in domain-specific workflows.
- **Trade-off / Downside**: It acts as an attractor for noisy or short queries, becoming the single largest category (48 of 200 golden examples) and lowering overall precision when edge cases trigger keywords from other classes.

---

### Decision 5: Use TF-IDF Lexical Cosine Matching for Historical Retrieval
- **Decision**: Implement unigram and bigram TF-IDF with sublinear term-frequency scaling and cosine similarity for historical resolution retrieval.
- **Why**: TF-IDF is completely deterministic, fast, requires zero external GPU infrastructure, has zero API network latency, and operates without dependency on third-party embeddings or quota limits.
- **Trade-off / Downside**: Lexical matching cannot capture semantic equivalence when customers use synonyms ("cab" vs. "car", "driver was rude" vs. "chauffeur behaved badly") without explicit lexical keyword matches.

---

### Decision 6: Pre-filter Historical Retrieval by Predicted Intent
- **Decision**: Filter the historical resolution candidate pool by the agent's predicted intent before computing cosine similarity.
- **Why**: Prevents irrelevant lexical overlaps. For instance, an inquiry saying "I lost my phone in the cab" could match a payment issue mentioning "phone number" unless constrained to driver or trip resolution procedures.
- **Trade-off / Downside**: If the upstream classifier misclassifies the message, retrieval is forced into an incorrect intent pool, propagating classification errors into retrieval.

---

### Decision 7: Establish a 0.20 Minimum Cosine Similarity Usability Threshold
- **Decision**: Set 0.20 as the threshold below which a nearest retrieved candidate is considered non-viable and exposed as `null`.
- **Why**: In sparse TF-IDF spaces, similarity scores below 0.20 usually indicate that only generic stop-words or coincidental single tokens matched. Exposing such candidates would lead to ungrounded or hallucinated replies.
- **Trade-off / Downside**: Approximately 33% of golden set inquiries fall below 0.20 against the 500-row demo corpus, driving up the escalation rate.

---

### Decision 8: Route Low-Similarity Cases (< 0.20) to `ESCALATE`
- **Decision**: Automatically trigger `ESCALATE` whenever similarity is below 0.20 or no usable historical match exists.
- **Why**: An AI support agent must adhere to the principle of "do no harm." When the system lacks historical resolution precedent, the safest operational decision is to route the customer to a human specialist.
- **Trade-off / Downside**: Suppresses the `AUTO_HANDLE` rate (only 15.50% auto-handled on the golden set), requiring human review for inquiries that might have had simple answers.

---

### Decision 9: Conservative Escalation on Account Access and Refund Processing
- **Decision**: Automatically escalate `account_access_issue`, `refund_request`, and `other_support_issue`, regardless of similarity score.
- **Why**: Account security (hacked accounts, password resets, deactivations) requires authenticated identity verification. Refund processing requires financial authorization. The prototype agent cannot securely perform account or banking mutations.
- **Trade-off / Downside**: Prevents fully automated resolution for straightforward account guidance (e.g. self-serve password reset links), keeping human agents in the loop.

---

### Decision 10: Commit a 500-Row Demo Corpus Instead of the Raw 3M-Row Dataset
- **Decision**: Package a clean, representative 500-row demo resolution CSV (`data/uber_resolution_demo.csv`) in the Git repository rather than uploading the full multi-gigabyte raw Kaggle archive.
- **Why**: Keeps the repository lightweight, fast to clone, and reproducible in standard CI/CD and local environments without downloading external gigabyte-scale datasets.
- **Trade-off / Downside**: Retrieval coverage is bounded by the 500 demo cases, resulting in lower similarity scores than would be obtained across the entire 51,590-pair corpus.

---

### Decision 11: AI-Assisted Pre-Labeling with 100% Human Verification for the Golden Set
- **Decision**: Construct the 200-row golden set by generating candidate annotations with LLM assistance, followed by manual human verification and correction of every single final label.
- **Why**: Accelerates initial dataset bootstrapping while ensuring ground truth is verified by human judgment rather than accepting noisy, unvalidated zero-shot model outputs.
- **Trade-off / Downside**: Annotator cognitive bias can occasionally be anchored by pre-labeled candidate suggestions on borderline cases between overlapping intents.

---

### Decision 12: Strict Information Isolation (Zero Label Leakage) During Evaluation
- **Decision**: Pass only `customer_message` to the agent pipeline. Never allow `gold_intent`, `ai_intent`, or `notes` to enter classification, retrieval, or LLM judge inputs.
- **Why**: Absolute prerequisite for valid benchmark science. Exposing ground truth labels or human comments to retrieval or draft generation produces artificially inflated evaluation metrics.
- **Trade-off / Downside**: The agent must rely purely on noisy, single-turn customer tweets without auxiliary metadata, reflecting true cold-start performance.

---

### Decision 13: Fixed Sample Size of 30 Examples with Fixed Random Seed 42 for Reply Judging
- **Decision**: Select a fixed subset of 30 examples (`seed=42`, sorted deterministically by `customer_tweet_id`) for LLM-as-a-judge and human evaluation.
- **Why**: Evaluating generative reply quality with human annotators across 200 examples is labor-intensive; 30 samples provides a tractable, reproducible cohort for inter-rater agreement without quota exhaustion.
- **Trade-off / Downside**: A sample of $N=30$ has wider confidence intervals than a full 200-example sample, meaning fine-grained statistical significance cannot be claimed.

---

### Decision 14: Honestly Report Missing LLM Judge Results Rather Than Fabricating Scores
- **Decision**: When `GEMINI_API_KEY` is not present in the environment, leave evaluation fields blank and clearly report the judge as unavailable.
- **Why**: Scientific integrity. Fabricating synthetic ratings or generating mock numbers violates fundamental engineering ethics and produces invalid agreement metrics.
- **Trade-off / Downside**: The evaluation report presents an incomplete LLM judge section until external API credentials are provided by the user.

---

### Decision 15: Explicitly Avoid Claiming Live Uber Integration
- **Decision**: Clearly position the system as an AI customer support prototype built on historical public Twitter data, explicitly denying live integration with Uber internal systems.
- **Why**: Real customer support automation requires integration with secure trip databases, dispatch telematics, payment gateways, and CRM systems (e.g. Zendesk, Salesforce). Claiming live execution would be misleading and factually false.
- **Trade-off / Downside**: Demonstrates routing recommendations and draft replies rather than end-to-end automated fulfillment of ticket actions.
