# Failure Analysis Report: Hiver AI Support Agent

- **Dataset**: `data/golden_set.csv` (200 human-verified examples)
- **Total Inquiries Evaluated**: 200
- **Misclassified Cases**: 78
- **Observed Accuracy**: 61.00%

---

## Executive Summary

The failure analysis reveals that classification errors predominantly concentrate around overlapping intent vocabularies (e.g., fare disputes requesting refunds, payment card failures overlapping with trip charges) and general conversational inquiries falling into or out of `other_support_issue`.

---

## Top 5 Classification Failure Patterns

### Pattern #22: Gold `other_support_issue` → Predicted `account_access_issue` (7 instances)

- **Failure Count**: 7 examples
- **Root Cause Hypothesis**: Overlapping terminology between 'other_support_issue' and 'account_access_issue' where keywords from 'account_access_issue' dominate the hit scoring.

**Observed Examples from Golden Set**:

1. **Message**: *"@2006 are you guys doing ride pass this month??? Would love to get that email has been very helpful to me and my family"*
   - **Similarity Score**: `0.2274`
   - **Routing Decision**: `AUTO_HANDLE`

2. **Message**: *"@Uber_Support is there an email address or phone number to contact you at so I'm not airing my problems out on twitter?"*
   - **Similarity Score**: `0.2205`
   - **Routing Decision**: `AUTO_HANDLE`

---

### Pattern #23: Gold `other_support_issue` → Predicted `app_or_technical_issue` (5 instances)

- **Failure Count**: 5 examples
- **Root Cause Hypothesis**: Overlapping terminology between 'other_support_issue' and 'app_or_technical_issue' where keywords from 'app_or_technical_issue' dominate the hit scoring.

**Observed Examples from Golden Set**:

1. **Message**: *"@115877 @115877 I appreciate an immediate response and support on this issue"*
   - **Similarity Score**: `0.1994`
   - **Routing Decision**: `ESCALATE`

2. **Message**: *"@Uber_Support U happen to have some kind of promo code I could use to save back that $8 im going for a 35min trip"*
   - **Similarity Score**: `0.3048`
   - **Routing Decision**: `ESCALATE`

---

### Pattern #4: Gold `app_or_technical_issue` → Predicted `account_access_issue` (5 instances)

- **Failure Count**: 5 examples
- **Root Cause Hypothesis**: App login crashes or authentication errors contain account-related terms ('sign in', 'login') that trigger account access instead of app technical errors.

**Observed Examples from Golden Set**:

1. **Message**: *"@115873 why can I add promo codes to my account?"*
   - **Similarity Score**: `0.3488`
   - **Routing Decision**: `AUTO_HANDLE`

2. **Message**: *"@115873 got an email that my next ride was 50% off b/c of a crazy long wait. But promo in my app will only work in the UK. Can someone help?"*
   - **Similarity Score**: `0.1981`
   - **Routing Decision**: `ESCALATE`

---

### Pattern #5: Gold `app_or_technical_issue` → Predicted `driver_issue` (4 instances)

- **Failure Count**: 4 examples
- **Root Cause Hypothesis**: Overlapping terminology between 'app_or_technical_issue' and 'driver_issue' where keywords from 'driver_issue' dominate the hit scoring.

**Observed Examples from Golden Set**:

1. **Message**: *"@Uber_Support Uber places phone calls to drivers through Google Hangouts rather than my sim phone service. How do I change this? P"*
   - **Similarity Score**: `0.1543`
   - **Routing Decision**: `ESCALATE`

2. **Message**: *"@115873 I was offered a renewal on my rider pass however the app didn't show the pass as expired till 1:00pm today. Why? 🤦🏻‍♂️"*
   - **Similarity Score**: `0.2668`
   - **Routing Decision**: `ESCALATE`

---

### Pattern #12: Gold `driver_issue` → Predicted `other_support_issue` (4 instances)

- **Failure Count**: 4 examples
- **Root Cause Hypothesis**: Overlapping terminology between 'driver_issue' and 'other_support_issue' where keywords from 'other_support_issue' dominate the hit scoring.

**Observed Examples from Golden Set**:

1. **Message**: *"@Uber_Support your cabs never reach on time . Y the hell you provide coupons"*
   - **Similarity Score**: `0.1879`
   - **Routing Decision**: `ESCALATE`

2. **Message**: *"@115873     Here's the photo, by the way, after ignoring all 37 of my phone calls https://t.co/QCUHBGF1mY"*
   - **Similarity Score**: `0.1648`
   - **Routing Decision**: `ESCALATE`

---

## Recommendations for Model Iteration

1. **Hierarchical or Multi-label Intent Disambiguation**:
   Decouple root causes (e.g. `fare_or_charge_issue`) from remediation actions (e.g. `refund_request`).
2. **Context-Aware Semantic Embeddings**:
   Augment keyword scoring with dense embeddings (e.g. Sentence-BERT or fine-tuned LLM) to capture semantic intent beyond surface n-grams.
3. **Dedicated Financial Intent Boundary**:
   Introduce disambiguation logic specifically separating payment gateway failures (`payment_issue`) from trip pricing adjustments (`fare_or_charge_issue`).
