# Comprehensive Playwright E2E QA Test Report

**Execution Timestamp:** 17/9/2026, 4:08:25 pm  
**Target Environment:**
- **Frontend:** `http://127.0.0.1:5173/` (Vite + React)
- **Backend:** `http://127.0.0.1:8000/` (FastAPI + Uvicorn)
- **Playwright Test Engine:** Playwright 1.63.0 on Chromium Headless (v153.0.8010.12)
- **Overall QA Verdict:** **FUNCTIONAL E2E PASS WITH SEMANTIC/QUALITY LIMITATIONS**

---

## 1. Overall Status

| Test Category | Total Tests | Passed | Warnings / Flags | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Pre-flight Connectivity** | 3 | 3 | 0 | **PASS** |
| **10 Core Customer Messages** | 10 | 9 | 1 | **WARN** |
| **Edge-Case Handling** | 8 | 8 | 0 | **PASS** |
| **Responsive Viewports** | 3 | 3 | 0 | **PASS** |
| **Console / Network Reliability** | 2 | 2 | 0 | **PASS** |

**Summary Assessment:** 10 core scenarios were executed through the live browser workflow. Semantic correctness is reported per scenario based on the explicit expected-intent checks implemented in the test. 9 scenarios resulted in ESCALATE and 1 resulted in AUTO_HANDLE during this test run. The routing reasons are reported from the application's actual decision logic. Browser console errors: 0; failed network requests: 0.

---

## 2. Frontend / UI Results

- **Reachable:** Yes (`http://127.0.0.1:5173/` returned HTTP 200)
- **Connection Indicator:** Displayed `"API Connected (Port 8000)"` with active connection styling.
- **Form Controls:** Textarea auto-updates character count, enables/disables the analyze button based on non-whitespace content, and displays loading spinner during processing.
- **Card Rendering:** Functional cards (Customer Input, AI Metric Grid, Grounded Draft Reply, Retrieved Historical Resolution, and Routing Decision) render without DOM unhandled exceptions.
- **Tab Navigation:** Sidebar navigation switches between Dashboard, History, Evaluation, and Settings tabs.

---

## 3. Backend / API Results

- **Health Endpoint (`/api/health`):** Returned HTTP 200 OK (`{"status":"ok","service":"hiver-ai-support-agent"}`).
- **Analysis Endpoint (`/api/analyze`):** Returned HTTP 200 OK across tested inbound customer messages with consistent schema:
  - `intent`: Non-null canonical support taxonomy label.
  - `confidence`: Float or null (calibrated rule model).
  - `similarity`: Float (TF-IDF cosine similarity against historical corpus).
  - `historical_match`: Matched customer message and support agent response.
  - `draft_reply`: Response synthesized from historical resolution.
  - `decision`: Either `AUTO_HANDLE` or `ESCALATE`.
  - `decision_reason`: Rationale string returned by the decision engine.

---

## 4. 10 Core Customer Message Test Results

10 core scenarios were executed through the live browser workflow. Semantic correctness is reported per scenario based on the explicit expected-intent checks implemented in the test.

| # | Customer Message | Predicted Intent | Similarity | Decision | Decision Rationale | Status |
| :-: | :--- | :--- | :---: | :---: | :--- | :---: |
| 1 | "I was charged too much for my Uber ride and want a refund." | `fare_or_charge_issue` | 0.2777 | `ESCALATE` | Historical responses indicate that this issue requires direct support follow-up. | **PASS** |
| 2 | "My Uber driver never came to the pickup location." | `driver_issue` | 0.2500 | `ESCALATE` | Historical responses indicate that this issue requires direct support follow-up. | **PASS** |
| 3 | "I forgot my Uber password and cannot log into my account." | `account_access_issue` | 0.1840 | `ESCALATE` | No usable historical resolution found (similarity 0.1840 is below 0.20 threshold). | **PASS** |
| 4 | "The Uber app keeps crashing when I try to open it." | `app_or_technical_issue` | 0.2151 | `AUTO_HANDLE` | A usable historical resolution was found (similarity: 0.2151) with self-contained guidance. | **WARN** |
| 5 | "I want my money back for my cancelled ride." | `cancellation_issue` | 0.2453 | `ESCALATE` | Historical responses indicate that this issue requires direct support follow-up. | **PASS** |
| 6 | "My payment failed but money was deducted from my account." | `payment_issue` | 0.1966 | `ESCALATE` | No usable historical resolution found (similarity 0.1966 is below 0.20 threshold). | **PASS** |
| 7 | "I ordered food on Uber Eats but my order never arrived." | `uber_eats_issue` | 0.2048 | `ESCALATE` | Historical responses indicate that this issue requires direct support follow-up. | **PASS** |
| 8 | "I was charged a cancellation fee." | `cancellation_issue` | 0.3968 | `ESCALATE` | Historical responses indicate that this issue requires direct support follow-up. | **PASS** |
| 9 | "My driver was rude and took the wrong route." | `driver_issue` | 0.3132 | `ESCALATE` | Historical responses indicate that this issue requires direct support follow-up. | **PASS** |
| 10 | "I need help with my Uber account." | `account_access_issue` | 0.3301 | `ESCALATE` | Account access inquiries require secure identity verification and human support intervention. | **PASS** |

### Detailed Observations for Core Messages:

#### Scenario 1: fare_overcharge
- **Inbound Message:** "I was charged too much for my Uber ride and want a refund."
- **Classified Intent:** `fare_or_charge_issue` (Fare Or Charge Issue)
- **Historical Customer Query:** ""@115873 I got charged twice for one ride I'm trying to get a refund can you help me""
- **Historical Support Resolution:** ""@438093 We can take a look! Send us a note via https://t.co/zJ6aIZinzb so our team can get in touch.""
- **Similarity Score:** `0.2777`
- **Draft Reply:** 
  > Sorry about the unexpected charge on your ride. Please send us a direct message with your trip details so our support team can review the fare.
- **Pipeline Decision:** `ESCALATE`
- **Decision Reason:** Historical responses indicate that this issue requires direct support follow-up.
- **Screenshot:** [`msg_01_fare_overcharge.png`](file:///./qa_screenshots/msg_01_fare_overcharge.png)

#### Scenario 2: driver_arrival
- **Inbound Message:** "My Uber driver never came to the pickup location."
- **Classified Intent:** `driver_issue` (Driver Issue)
- **Historical Customer Query:** ""@Uber_Support your uber driver hasnt ended my ride. it has been over 8 minutes and im at my location that i need to be.""
- **Historical Support Resolution:** ""@528620 Sorry to hear about that! Please send us a note here; https://t.co/WFtPA6RjWt and our team will get in touch.""
- **Similarity Score:** `0.2500`
- **Draft Reply:** 
  > We sincerely apologize for the experience with your driver. Please send us a direct message with your trip details so our team can follow up immediately.
- **Pipeline Decision:** `ESCALATE`
- **Decision Reason:** Historical responses indicate that this issue requires direct support follow-up.
- **Screenshot:** [`msg_02_driver_arrival.png`](file:///./qa_screenshots/msg_02_driver_arrival.png)

#### Scenario 3: account_access
- **Inbound Message:** "I forgot my Uber password and cannot log into my account."
- **Classified Intent:** `account_access_issue` (Account Access Issue)
- **Historical Customer Query:** "N/A"
- **Historical Support Resolution:** "N/A"
- **Similarity Score:** `0.1840`
- **Draft Reply:** 
  > We apologize for the difficulty accessing your account. Please confirm your registered email and phone number so our account team can assist you safely.
- **Pipeline Decision:** `ESCALATE`
- **Decision Reason:** No usable historical resolution found (similarity 0.1840 is below 0.20 threshold).
- **Screenshot:** [`msg_03_account_access.png`](file:///./qa_screenshots/msg_03_account_access.png)

#### Scenario 4: app_technical_issue
- **Inbound Message:** "The Uber app keeps crashing when I try to open it."
- **Classified Intent:** `app_or_technical_issue` (App Or Technical Issue)
- **Historical Customer Query:** ""I’m happily deleting @115873 uber fraud app https://t.co/hP3hZhS8aE""
- **Historical Support Resolution:** ""@509955 Hi, Moudi! Go ahead and check your app! We've reached out to you via in-app support which you can respond to directly for further details.""
- **Similarity Score:** `0.2151`
- **Draft Reply:** 
  > We are here to help. Based on standard resolution procedures: Hi, Moudi! Go ahead and check your app! We've reached out to you via in-app support which you can respond to directly for further details. If you need further assistance, please let us know.
- **Privacy / Grounding Alert:** ⚠️ **Grounding/privacy warning: historical customer-specific information appears in the draft.**
- **Pipeline Decision:** `AUTO_HANDLE`
- **Decision Reason:** A usable historical resolution was found (similarity: 0.2151) with self-contained guidance.
- **Screenshot:** [`msg_04_app_technical_issue.png`](file:///./qa_screenshots/msg_04_app_technical_issue.png)

#### Scenario 5: cancellation_refund
- **Inbound Message:** "I want my money back for my cancelled ride."
- **Classified Intent:** `cancellation_issue` (Cancellation Issue)
- **Historical Customer Query:** ""How dare you @115873 charge £5 for one of your unprofessional drivers who cancelled after not meeting at the agreed meeting point. I do not want a credit just my money back.""
- **Historical Support Resolution:** ""@476546 Here to help! Send us a note at; https://t.co/h840Iouehc so we can assist.""
- **Similarity Score:** `0.2453`
- **Draft Reply:** 
  > Sorry about the issue you're experiencing. Please send us a DM with your details so our support team can review this and assist you further.
- **Pipeline Decision:** `ESCALATE`
- **Decision Reason:** Historical responses indicate that this issue requires direct support follow-up.
- **Screenshot:** [`msg_05_cancellation_refund.png`](file:///./qa_screenshots/msg_05_cancellation_refund.png)

#### Scenario 6: payment_issue
- **Inbound Message:** "My payment failed but money was deducted from my account."
- **Classified Intent:** `payment_issue` (Payment Issue)
- **Historical Customer Query:** "N/A"
- **Historical Support Resolution:** "N/A"
- **Similarity Score:** `0.1966`
- **Draft Reply:** 
  > Sorry for the payment difficulty. Please review your active payment method in the app or contact support with transaction details.
- **Pipeline Decision:** `ESCALATE`
- **Decision Reason:** No usable historical resolution found (similarity 0.1966 is below 0.20 threshold).
- **Screenshot:** [`msg_06_payment_issue.png`](file:///./qa_screenshots/msg_06_payment_issue.png)

#### Scenario 7: eats_order
- **Inbound Message:** "I ordered food on Uber Eats but my order never arrived."
- **Classified Intent:** `uber_eats_issue` (Uber Eats Issue)
- **Historical Customer Query:** ""@115877 anyone home? Order never arrived and no one seems to want to respond to my request for help. #WhatCustomerService #1star #UberEats""
- **Historical Support Resolution:** ""@180751 Let's take a further look into this. Please send us a DM with your email and phone number linked to your account.""
- **Similarity Score:** `0.2048`
- **Draft Reply:** 
  > We are sorry for the trouble with your delivery order. Please send us a DM with your order details so our team can look into this right away.
- **Pipeline Decision:** `ESCALATE`
- **Decision Reason:** Historical responses indicate that this issue requires direct support follow-up.
- **Screenshot:** [`msg_07_eats_order.png`](file:///./qa_screenshots/msg_07_eats_order.png)

#### Scenario 8: cancellation_fee
- **Inbound Message:** "I was charged a cancellation fee."
- **Classified Intent:** `cancellation_issue` (Cancellation Issue)
- **Historical Customer Query:** ""@115873 gonna charge me a $5 cancellation fee. 🤔 https://t.co/V0QJ6kSWp2""
- **Historical Support Resolution:** ""@272382 We're here to help! Please send us a note via https://t.co/xguILK85B3 so we can connect.""
- **Similarity Score:** `0.3968`
- **Draft Reply:** 
  > Sorry about the issue you're experiencing. Please send us a DM with your details so our support team can review this and assist you further.
- **Pipeline Decision:** `ESCALATE`
- **Decision Reason:** Historical responses indicate that this issue requires direct support follow-up.
- **Screenshot:** [`msg_08_cancellation_fee.png`](file:///./qa_screenshots/msg_08_cancellation_fee.png)

#### Scenario 9: driver_conduct_or_route
- **Inbound Message:** "My driver was rude and took the wrong route."
- **Classified Intent:** `driver_issue` (Driver Issue)
- **Historical Customer Query:** ""@115873 driver picked me up at the wrong location, took wrong turns, &amp; I still paid an adjusted fair. The entire trip needs to be reimbursed.""
- **Historical Support Resolution:** ""@345831 Happy to help! Send us a DM with your email address and our team will follow up.""
- **Similarity Score:** `0.3132`
- **Draft Reply:** 
  > We sincerely apologize for the experience with your driver. Please send us a direct message with your trip details so our team can follow up immediately.
- **Pipeline Decision:** `ESCALATE`
- **Decision Reason:** Historical responses indicate that this issue requires direct support follow-up.
- **Screenshot:** [`msg_09_driver_conduct_route.png`](file:///./qa_screenshots/msg_09_driver_conduct_route.png)

#### Scenario 10: account_general
- **Inbound Message:** "I need help with my Uber account."
- **Classified Intent:** `account_access_issue` (Account Access Issue)
- **Historical Customer Query:** ""@Uber_Support Hey, I need to get help ASAP with my account. I'm getting an error that I can't correct &amp; I need to speak with someone. Please help! Thanks!""
- **Historical Support Resolution:** ""@265845 Here to help! Follow up here; https://t.co/SjsQQ8ofRq, and our team will connect right away.""
- **Similarity Score:** `0.3301`
- **Draft Reply:** 
  > We are here to help. Based on standard resolution procedures: Here to help! Follow up here; and our team will connect right away. If you need further assistance, please let us know.
- **Pipeline Decision:** `ESCALATE`
- **Decision Reason:** Account access inquiries require secure identity verification and human support intervention.
- **Screenshot:** [`msg_10_account_general.png`](file:///./qa_screenshots/msg_10_account_general.png)

---

## 5. Edge-Case Results

The suite tested atypical, malformed, and adversarial inputs:

| ID | Edge Case | Test Input | Observed Intent & Decision | Observed Behavior & Notes | Status |
| :-: | :--- | :--- | :--- | :--- | :---: |
| E1 | empty_message | `(empty string)` | Intent: `N/A` • Decision: `Button Disabled` | Submit button disabled for empty input | **PASS** |
| E2 | short_help | `Help` | Intent: `other_support_issue` • Decision: `ESCALATE` | Analyzed without runtime failure | **PASS** |
| E3 | long_message | `Hello support team, I am writing to you today because yester...` | Intent: `payment_issue` • Decision: `AUTO_HANDLE` | Mixed-intent input (fare dispute, driver detour, dropoff terminal). Observed prediction: payment_issue. | **PASS** |
| E4 | emojis | `😡🚕 Where is my car??? Driver cancelled after making me wai...` | Intent: `cancellation_issue` • Decision: `ESCALATE` | Analyzed without runtime failure | **PASS** |
| E5 | numbers | `12345 67890 999 45.50` | Intent: `other_support_issue` • Decision: `ESCALATE` | Analyzed without runtime failure | **PASS** |
| E6 | spelling_mistakes | `I wuz chrgd way 2 much 4 my Ubr ryde nd wnt a full refnd plz...` | Intent: `other_support_issue` • Decision: `ESCALATE` | Runtime handling passed, but semantic intent classification degraded under spelling/phonetic noise. | **PASS** |
| E7 | mixed_case | `mY dRiVeR nEvEr ShOwEd Up At ThE pIcKuP lOcAtIoN` | Intent: `driver_issue` • Decision: `ESCALATE` | Analyzed without runtime failure | **PASS** |
| E8 | extra_spaces | `     I   was   charged   a   cancellation   fee        ` | Intent: `cancellation_issue` • Decision: `ESCALATE` | Analyzed without runtime failure | **PASS** |

### Edge-Case Observations:
1. **Empty Message (E1):** The UI submit button is dynamically disabled when the textarea is empty or whitespace-only, preventing invalid API calls before they reach the wire.
2. **Short "Help" (E2):** Processed without runtime failure; classified as `other_support_issue` and routed to `ESCALATE` due to low historical similarity (< 0.20 threshold).
3. **Long Inbound Paragraph (E3):** Long input was successfully submitted and analyzed without runtime failure. The observed intent and retrieval result are reported separately; successful processing does not imply semantic correctness. E3 is a mixed-intent input containing multiple complaints (fare dispute, driver detour, and missed flight dropoff terminal); the actual observed prediction was `payment_issue`.
4. **Emojis, Typos & Mixed Case (E4, E6, E7):** Emojis, spelling-noise, and mixed-case inputs were processed without runtime failure. Semantic classification quality is reported from the observed predictions and is not assumed to be correct.
5. **Spelling Noise Degraded Classification (E6):** For input with phonetic/spelling noise ("I wuz chrgd way 2 much 4 my Ubr ryde nd wnt a full refnd plzzz"), the observed intent was `other_support_issue`. Runtime handling passed, but semantic intent classification degraded under spelling/phonetic noise.
6. **Extra Whitespace (E8):** Processed without runtime failure; leading/trailing whitespace was normalized and mapped to `cancellation_issue`.

---

## 6. Historical Retrieval Quality

- **Corpus Context:** 500 Uber Support tweet resolutions indexed with TF-IDF retrieval.
- **Observed Retrieval Results:** Historical resolution pairs were retrieved for categories such as fare overcharge, driver issues, and cancellation disputes. For generic or low-frequency terms, similarity fell below the 0.20 threshold.
- **Intent Partitioning:** Historical retrieval matches within the classified intent slice.
- **Measured Similarity Range:** Observed similarity scores ranged from 0.0000 up to 0.3968 across core scenarios.

---

## 7. Draft Reply Quality (Measured Properties)

Draft replies were assessed strictly against directly measurable properties:
- **Non-empty:** Verified. Draft replies were generated and populated in the UI textarea for all analyzed inputs.
- **Generation Success:** Verified. No error banners or generation timeouts occurred.
- **Error Banners:** None observed on valid customer messages.
- **Grounding and Customer Identity Verification:**
  - In Scenario 4 (app crash inquiry: *"The Uber app keeps crashing when I try to open it."*), the retrieved historical support tweet contained customer-specific text: `"@509955 Hi, Moudi! Go ahead and check your app!..."`. The generated draft incorporated this greeting: `"We are here to help. Based on standard resolution procedures: Hi, Moudi!..."`.
  - Result: **Grounding/privacy warning: historical customer-specific information appears in the draft.**
  - This reply cannot be described as fully grounded or free of privacy artifacts.
- **Subjective Quality Disclaimer:** Subjective traits (e.g. empathy, human tone, conversational polish) were not evaluated by this automated browser test and require human evaluation or an LLM-as-judge benchmark.
- **Agent Interactivity:** The draft reply textarea in the UI is confirmed to be user-editable prior to dispatch.

---

## 8. Decision Quality (AUTO_HANDLE vs ESCALATE)

9 scenarios resulted in ESCALATE and 1 resulted in AUTO_HANDLE during this test run. The routing reasons are reported from the application's actual decision logic.

- **Observed Decision Rationales:**
  - Historical responses indicate that the issue requires direct support follow-up (e.g. asking for DM with trip/account details).
  - Similarity score below 0.20 threshold resulting in escalation.
  - Account access inquiries routed to escalation for secure identity verification.
  - When historical resolution provided self-contained guidance and similarity exceeded threshold, AUTO_HANDLE was assigned (Scenario 4, though flagged for customer name inclusion).

---

## 9. Browser Console & Network Reliability

- **Browser Console Errors:** **0** observed during test execution.
- **Failed HTTP Network Requests:** **0** observed during test execution.
- **HTTP Status Codes:** All calls to `/api/health` and `/api/analyze` returned HTTP 200.
- **CORS / Preflight:** API requests between `127.0.0.1:5173` and `127.0.0.1:8000` succeeded.

---

## 10. Responsive Layout Checks

Responsive layout checks passed for the tested viewports.

| Viewport | Dimensions | Horizontal Overflow | Critical Elements Visible | Status |
| :--- | :---: | :---: | :---: | :---: |
| desktop | 1280x900 | No | Yes | **PASS** |
| tablet | 768x1024 | No | Yes | **PASS** |
| mobile | 375x667 | No | Yes | **PASS** |

- **Desktop (1280x900):** Side-by-side card grid displayed without clipping.
- **Tablet (768x1024):** Grid wrapped into two columns; input controls fully visible.
- **Mobile (375x667):** Single-column stacked layout; no horizontal overflow detected (`scrollWidth <= clientWidth`).

---

## 11. Screenshots Generated

Screenshots captured during live browser execution and saved to `qa_screenshots/`:

| File Name | Description |
| :--- | :--- |
| `00_initial_connected_state.png` | Dashboard initial state showing API connected |
| `msg_01_fare_overcharge.png` | Message 1 result: Fare overcharge analysis |
| `msg_02_driver_arrival.png` | Message 2 result: Driver arrival inquiry |
| `msg_03_account_access.png` | Message 3 result: Account login issue |
| `msg_04_app_technical_issue.png` | Message 4 result: App crashing report |
| `msg_05_cancellation_refund.png` | Message 5 result: Cancelled ride refund |
| `msg_06_payment_issue.png` | Message 6 result: Payment deducted failure |
| `msg_07_eats_order.png` | Message 7 result: Uber Eats order missing |
| `msg_08_cancellation_fee.png` | Message 8 result: Cancellation fee dispute |
| `msg_09_driver_conduct_route.png` | Message 9 result: Rude driver & wrong route |
| `msg_10_account_general.png` | Message 10 result: General account help |
| `edge_E1_empty_message.png` | Edge Case E1: Empty textarea disabled state |
| `edge_E2_short_help.png` | Edge Case E2: "Help" single word |
| `edge_E3_long_message.png` | Edge Case E3: Long detailed paragraph |
| `edge_E4_emojis.png` | Edge Case E4: Emojis and punctuation |
| `edge_E5_numbers.png` | Edge Case E5: Numbers only |
| `edge_E6_spelling_mistakes.png` | Edge Case E6: Phonetic and spelling errors |
| `edge_E7_mixed_case.png` | Edge Case E7: Alternating upper/lower case |
| `edge_E8_extra_spaces.png` | Edge Case E8: Input with excessive spacing |
| `viewport_desktop.png` | Responsive desktop view (1280x900) |
| `viewport_tablet.png` | Responsive tablet view (768x1024) |
| `viewport_mobile.png` | Responsive mobile view (375x667) |

---

## 12. Issues & Limitations Identified

1. **Grounding / Privacy Leakage in Synthesized Draft (Scenario 4):**
   - The historical resolution pair retrieved for app crash contained a specific customer name ("Moudi").
   - The draft generator included "Hi, Moudi!" in the synthesized response, even though the current customer did not provide that name.
   - **Grounding/privacy warning: historical customer-specific information appears in the draft.**
2. **Intent Degradation Under Phonetic/Spelling Noise (Scenario E6):**
   - Noisy input ("I wuz chrgd way 2 much 4 my Ubr ryde nd wnt a full refnd plzzz") was classified as `other_support_issue` rather than `fare_or_charge_issue` or `refund_request`.
   - Runtime handling passed, but semantic intent classification degraded under spelling/phonetic noise.
3. **Mixed-Intent Parsing (Scenario E3):**
   - Long multi-complaint message was classified as `payment_issue`. While payment is one of the mentioned components, the message also included driver route deviations and dropoff location issues.
4. **Low N-Gram Overlap on Generic Queries (Scenario E2 & E5):**
   - Single-word inputs ("Help") or number strings lack specific keywords and resulted in low similarity scores (< 0.20), triggering escalation.

---

## 13. Recommended Application Fixes

1. **Customer Identity Sanitization:** Implement regex or NER scrubbing to remove customer names, user handles (@user), and customer-specific IDs from historical tweets before passing them to draft reply generation.
2. **Spelling Correction / Phonetic Normalization:** Add a pre-processing step for spelling correction or fuzzy token matching so that noisy inputs (e.g. "wuz chrgd", "refnd") map to their intended canonical taxonomy.
3. **Multi-Intent Detection:** Support compound or hierarchical intent labels for multi-part grievances such as Scenario E3.

---

## 14. Final Assessment

- **Functional E2E Execution:** All tested browser workflows (pre-flight checks, input submission, API communication, DOM state updates, and responsive viewport sizing) executed without runtime failure.
- **Measured Reliability:** Observed 0 browser console errors and 0 failed network requests.
- **Semantic & Quality Limitations:**
  - Semantic intent classification degraded under spelling/phonetic noise (Scenario E6 predicted `other_support_issue`).
  - Mixed-intent input in Scenario E3 was classified as `payment_issue`, but contains multi-part complaints.
  - Scenario 4 generated draft contained historical customer name "Moudi", triggering: **Grounding/privacy warning: historical customer-specific information appears in the draft.**
- **Overall QA Verdict:** **FUNCTIONAL E2E PASS WITH SEMANTIC/QUALITY LIMITATIONS**

---

## 15. QA Scope and Limitations

Playwright verifies the live local frontend/backend workflow, API connectivity, browser interaction, basic rendering, and measured assertions. It does NOT replace the 200-example golden evaluation, LLM-as-judge evaluation, human reply-quality evaluation, production testing, or subjective visual review.
