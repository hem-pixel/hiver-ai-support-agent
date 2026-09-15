\# Hiver AI Support Agent — Evaluation



\## 1. Dataset



This project uses the Kaggle Customer Support on Twitter dataset.



For the Uber Support experiment, historical conversations were reconstructed using the tweet relationship fields:



\- `response\_tweet\_id`

\- `in\_response\_to\_tweet\_id`

\- `inbound`

\- `text`



The selected brand is Uber, using conversations involving `@Uber\_Support`.



The customer-message pool contains approximately 55K strongly linked inbound customer messages.



\## 2. Intent Taxonomy



The support messages are classified into 10 intents:



1\. `fare\_or\_charge\_issue`

2\. `refund\_request`

3\. `driver\_issue`

4\. `trip\_issue`

5\. `cancellation\_issue`

6\. `account\_access\_issue`

7\. `payment\_issue`

8\. `app\_or\_technical\_issue`

9\. `uber\_eats\_issue`

10\. `other\_support\_issue`



The taxonomy was intentionally kept small so that the agent can make consistent routing decisions.



\## 3. Golden Evaluation Set



A 200-example golden set was created from the Uber customer-message pool.



Sampling was performed from the available customer messages rather than selecting only obvious keyword matches.



The initial labels were AI-assisted for efficiency and were then human-verified. The final `gold\_intent` field contains a label for all 200 examples.



Final verification status:



\- Total examples: 200

\- Missing labels: 0

\- Intents: 10



\### Distribution



| Intent | Count |

|---|---:|

| other\_support\_issue | 48 |

| driver\_issue | 38 |

| account\_access\_issue | 24 |

| uber\_eats\_issue | 22 |

| fare\_or\_charge\_issue | 15 |

| app\_or\_technical\_issue | 15 |

| cancellation\_issue | 14 |

| refund\_request | 12 |

| payment\_issue | 8 |

| trip\_issue | 4 |



The golden set is stored at:



`D:\\twcs\\hiver\_data\\golden\_set.csv`



\## 4. Evaluation Protocol



Two simple classification baselines were evaluated using the same stratified train/test split:



\- Test size: 25%

\- Test examples: 50

\- Random state: 42

\- Stratification by gold intent



\### Baseline 1 — TF-IDF + Logistic Regression



The first baseline converts customer messages into TF-IDF word n-gram features and trains a Logistic Regression classifier.



Accuracy:



\*\*40.00%\*\*



\### Baseline 2 — Keyword Rule-Based



The second baseline uses deterministic intent-specific keyword rules.



Accuracy:



\*\*64.00%\*\*



Macro F1:



\*\*0.59\*\*



Weighted F1:



\*\*0.64\*\*



The rule-based baseline therefore outperformed the TF-IDF baseline by 24 percentage points in accuracy on this holdout.



\## 5. Rule-Based Baseline — Per-Intent Results



| Intent | Precision | Recall | F1 |

|---|---:|---:|---:|

| account\_access\_issue | 0.56 | 0.83 | 0.67 |

| app\_or\_technical\_issue | 0.33 | 0.25 | 0.29 |

| cancellation\_issue | 0.50 | 0.33 | 0.40 |

| driver\_issue | 0.82 | 0.90 | 0.86 |

| fare\_or\_charge\_issue | 0.50 | 0.25 | 0.33 |

| other\_support\_issue | 0.62 | 0.67 | 0.64 |

| payment\_issue | 0.00 | 0.00 | 0.00 |

| refund\_request | 1.00 | 0.67 | 0.80 |

| trip\_issue | 1.00 | 1.00 | 1.00 |

| uber\_eats\_issue | 1.00 | 0.80 | 0.89 |



\## 6. Historical Resolution Retrieval



Historical Uber customer/support pairs were reconstructed from the original dataset.



The resulting resolution dataset contains:



\*\*51,590 unique customer → Uber Support response pairs.\*\*



The retriever uses TF-IDF similarity after filtering historical examples by predicted intent.



This prevents a message containing the word "refund" from automatically retrieving unrelated refund examples when the underlying issue is primarily a fare or charge problem.



\## 7. Agent Decision Logic



The prototype follows this flow:



Customer message  

→ intent classification  

→ intent-filtered historical retrieval  

→ similarity scoring  

→ grounded draft reply  

→ auto-handle or escalate



The agent escalates when:



\- the historical response requires direct support follow-up, such as asking the customer to send a DM; or

\- no sufficiently similar historical resolution is found.



Otherwise, the agent can mark the case as `AUTO\_HANDLE`.



\## 8. Example



Customer:



> I was charged too much for my Uber ride and want a refund



Predicted intent:



`fare\_or\_charge\_issue`



Best historical similarity:



`0.3484`



The retrieved historical case involved an incorrect Uber charge and refund request.



Because the historical support response asked the customer to contact Uber directly, the agent produces a grounded support reply and chooses:



`ESCALATE`



Reason:



`Historical responses indicate that this issue requires direct support follow-up.`



\## 9. Current Evaluation Limitation



The independent Gemini prediction run was rate-limited by the available API quota.



Therefore, only 10 independent Gemini predictions are currently available.



These 10 predictions are retained separately in:



`D:\\twcs\\hiver\_data\\golden\_predictions.csv`



They are \*\*not\*\* treated as a 200-example model evaluation.



The 64% and 40% headline numbers above are baseline results on the 50-example holdout and should not be presented as final AI-agent accuracy.



\## 10. What Is Misleading About My Headline Number?



The 64% accuracy number is useful as a baseline, but it can be misleading if presented as overall agent quality.



First, it is measured on only 50 test examples from a 200-example golden set. Second, the dataset is imbalanced, with `other\_support\_issue` and `driver\_issue` making up a large portion of the sample. Third, classification accuracy does not measure whether a generated reply is actually helpful or whether an escalation decision is appropriate.



A stronger evaluation should measure intent classification, reply quality, and escalation quality separately on a larger independent evaluation set.



\## 11. Next Steps



For the next iteration:



1\. Expand the golden set and independent model predictions.

2\. Add LLM-as-judge evaluation for reply relevance, grounding, and helpfulness.

3\. Measure agreement between the LLM judge and human ratings.

4\. Improve difficult intent boundaries such as fare vs refund and payment vs fare.

5\. Add explicit detection for generic historical replies that do not represent an actual resolution.

6\. Evaluate escalation precision and recall separately from intent accuracy.

