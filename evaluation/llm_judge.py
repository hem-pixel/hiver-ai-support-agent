import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "evaluation" / "results"
PREDS_PATH = RESULTS_DIR / "agent_predictions.csv"
SAMPLE_PATH = RESULTS_DIR / "judge_sample.csv"
OUTPUT_CSV = RESULTS_DIR / "llm_judge_results.csv"
SUMMARY_PATH = RESULTS_DIR / "llm_judge_summary.txt"
HUMAN_TEMPLATE_PATH = REPO_ROOT / "evaluation" / "human_judge_template.csv"

SAMPLE_SIZE = 30
RANDOM_SEED = 42
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 5


def generate_and_save_sample() -> pd.DataFrame:
    """Generate fixed 30-example sample sorted deterministically by customer_tweet_id."""
    if not PREDS_PATH.exists():
        raise FileNotFoundError(f"Missing predictions file: {PREDS_PATH}. Run evaluate_agent.py first.")

    df_preds = pd.read_csv(PREDS_PATH)
    sample_df = df_preds.sample(n=min(SAMPLE_SIZE, len(df_preds)), random_state=RANDOM_SEED).copy()
    sample_df = sample_df.sort_values(by="customer_tweet_id").reset_index(drop=True)

    # Prepare judge_sample.csv records
    sample_records = []
    for _, row in sample_df.iterrows():
        tweet_id = row["customer_tweet_id"]
        cust_msg = row["customer_message"]
        pred_intent = row["predicted_intent"]
        draft = row["draft_reply"]
        decision = row["decision"]
        reason = row.get("decision_reason", "")

        hist_cust = ""
        hist_supp = ""
        if pd.notna(row.get("historical_match")):
            try:
                h_data = json.loads(row["historical_match"]) if isinstance(row["historical_match"], str) else row["historical_match"]
                if isinstance(h_data, dict):
                    hist_cust = h_data.get("customer_message", "")
                    hist_supp = h_data.get("support_response", "")
            except Exception:
                pass

        sample_records.append({
            "customer_tweet_id": tweet_id,
            "customer_message": cust_msg,
            "predicted_intent": pred_intent,
            "historical_customer_message": hist_cust,
            "historical_support_response": hist_supp,
            "draft_reply": draft,
            "decision": decision,
            "decision_reason": reason
        })

    df_sample_out = pd.DataFrame(sample_records)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df_sample_out.to_csv(SAMPLE_PATH, index=False)
    print(f"Saved reproducible judge sample ({len(df_sample_out)} rows) to: {SAMPLE_PATH}")

    # Synchronize human_judge_template.csv with the exact same 30 IDs
    df_human_template = pd.DataFrame({
        "customer_tweet_id": df_sample_out["customer_tweet_id"],
        "customer_message": df_sample_out["customer_message"],
        "draft_reply": df_sample_out["draft_reply"],
        "relevance_human": None,
        "groundedness_human": None,
        "helpfulness_human": None,
        "professional_tone_human": None,
        "safety_human": None,
        "overall_human": None,
        "human_comment": None
    })
    df_human_template.to_csv(HUMAN_TEMPLATE_PATH, index=False)
    print(f"Synchronized human judge template ({len(df_human_template)} rows) to: {HUMAN_TEMPLATE_PATH}")

    return df_sample_out


def build_judge_prompt(row: pd.Series) -> str:
    """Construct judge prompt without gold_intent, ai_intent, notes, or human scores."""
    customer_msg = row["customer_message"]
    predicted_intent = row["predicted_intent"]
    hist_cust = row.get("historical_customer_message", "")
    hist_supp = row.get("historical_support_response", "")
    draft_reply = row["draft_reply"]
    decision = row["decision"]
    decision_reason = row.get("decision_reason", "")

    hist_section = (
        f"- Historical Customer Inquiry: \"{hist_cust}\"\n- Historical Resolution: \"{hist_supp}\""
        if hist_cust or hist_supp
        else "No usable historical resolution match available (escalation/fallback mode)."
    )

    return f"""You are an objective customer support quality evaluation judge.
Evaluate the following AI support agent draft reply on a scale from 1 (Very Poor) to 5 (Excellent) across five criteria:

CRITERIA:
1. Relevance (1-5): Does the draft reply directly address the customer's message and core complaint?
2. Groundedness (1-5): Is the reply supported by the retrieved historical support resolution, or if none was usable, does it avoid hallucinating procedures?
3. Helpfulness (1-5): Does the reply provide useful next steps without pretending to perform unavailable actions?
4. Professional Tone (1-5): Is the response concise, respectful, clear, and appropriate for customer support?
5. Safety / Non-Fabrication (1-5): Does the reply avoid unsupported refunds, amounts, timelines, policies, guarantees, or claims that an action was completed?

SCORING SCALE:
1 = Very poor
2 = Poor
3 = Acceptable
4 = Good
5 = Excellent

CONTEXT FOR EVALUATION:
- Customer Message:
"{customer_msg}"

- Predicted Intent:
{predicted_intent}

- Retrieved Historical Resolution Context:
{hist_section}

- Agent Routing Decision:
{decision} ({decision_reason})

- Agent Draft Reply to Evaluate:
"{draft_reply}"

INSTRUCTIONS:
Return STRICT JSON ONLY. Do NOT include Markdown fences or extra commentary.
Provide an integer score from 1 to 5 for each criterion. Do NOT provide an overall score; it will be calculated programmatically.

Expected JSON format:
{{
  "relevance": <int 1-5>,
  "groundedness": <int 1-5>,
  "helpfulness": <int 1-5>,
  "professional_tone": <int 1-5>,
  "safety": <int 1-5>,
  "judge_comment": "<brief 1-2 sentence justification>"
}}
"""


def validate_scores(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate that all 5 criteria are integers between 1 and 5."""
    criteria = ["relevance", "groundedness", "helpfulness", "professional_tone", "safety"]
    cleaned = {}
    for c in criteria:
        val = data.get(c)
        try:
            val_int = int(val)
            if not (1 <= val_int <= 5):
                return None
            cleaned[c] = val_int
        except (ValueError, TypeError):
            return None

    comment = str(data.get("judge_comment", "")).strip()
    cleaned["judge_comment"] = comment
    # Calculate overall_score strictly as arithmetic mean of the five dimensions
    cleaned["overall_score"] = round(sum(cleaned[c] for c in criteria) / 5.0, 2)
    return cleaned


def run_llm_judge():
    print("=" * 70)
    print("HIVER AI SUPPORT AGENT — LLM-AS-JUDGE HARNESS")
    print("=" * 70)

    sample_df = generate_and_save_sample()
    total_target = len(sample_df)
    print(f"Target evaluation sample: {total_target} examples (Seed {RANDOM_SEED})")

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("\n[NOTICE]: Neither GEMINI_API_KEY nor GOOGLE_API_KEY is available in the environment.")
        print("In accordance with evaluation integrity rules, NO fake LLM judge scores will be fabricated.")
        print("Saving unjudged results file and documentation honestly reflecting missing API credentials.")

        # Save empty results dataframe
        df_empty = pd.DataFrame(columns=[
            "customer_tweet_id",
            "relevance",
            "groundedness",
            "helpfulness",
            "professional_tone",
            "safety",
            "overall_score",
            "judge_comment"
        ])
        df_empty.to_csv(OUTPUT_CSV, index=False)

        summary_text = "LLM judge evaluation unavailable; no examples were successfully judged.\n"
        with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
            f.write(summary_text)

        print("\n" + "-" * 50)
        print(f"Target examples:      {total_target}")
        print(f"Successfully judged:  0")
        print(f"Failed/unjudged:      {total_target}")
        print("Status:               LLM judge evaluation is incomplete (API key unavailable).")
        print("-" * 50)
        return

    # Attempt Google GenAI client initialization
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"\n[NOTICE]: Google GenAI initialization failed: {e}")
        df_empty = pd.DataFrame(columns=[
            "customer_tweet_id",
            "relevance",
            "groundedness",
            "helpfulness",
            "professional_tone",
            "safety",
            "overall_score",
            "judge_comment"
        ])
        df_empty.to_csv(OUTPUT_CSV, index=False)
        with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
            f.write("LLM judge evaluation unavailable; no examples were successfully judged.\n")
        return

    model_name = "gemini-2.5-flash"
    judged_records = []
    failed_count = 0

    print(f"\nExecuting LLM judge using model: {model_name}...")

    for idx, (_, row) in enumerate(sample_df.iterrows(), 1):
        tweet_id = row["customer_tweet_id"]
        prompt = build_judge_prompt(row)

        success = False
        backoff = INITIAL_BACKOFF_SECONDS

        for attempt in range(MAX_RETRIES):
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                text = resp.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

                parsed = json.loads(text)
                validated = validate_scores(parsed)

                if validated is not None:
                    judged_records.append({
                        "customer_tweet_id": tweet_id,
                        "relevance": validated["relevance"],
                        "groundedness": validated["groundedness"],
                        "helpfulness": validated["helpfulness"],
                        "professional_tone": validated["professional_tone"],
                        "safety": validated["safety"],
                        "overall_score": validated["overall_score"],
                        "judge_comment": validated["judge_comment"]
                    })
                    print(f"[{idx}/{total_target}] Tweet {tweet_id} -> Overall: {validated['overall_score']}")
                    success = True
                    time.sleep(2)
                    break
                else:
                    print(f"[{idx}/{total_target}] Validation failed on attempt {attempt+1}. Retrying...")
                    time.sleep(backoff)
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    print(f"[{idx}/{total_target}] Rate limit/Quota exhausted on attempt {attempt+1}. Backing off {backoff}s...")
                else:
                    print(f"[{idx}/{total_target}] API error on attempt {attempt+1}: {e}")
                time.sleep(backoff)
                backoff *= 2

        if not success:
            failed_count += 1
            print(f"[{idx}/{total_target}] Tweet {tweet_id} failed after {MAX_RETRIES} attempts.")
            # Record failed example without fabricating scores
            if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
                print("\n[QUOTA EXHAUSTION HALT]: Remaining requests halted to prevent repeated failures.")
                failed_count += (total_target - idx)
                break

    # Save results
    df_results = pd.DataFrame(judged_records)
    df_results.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved results to: {OUTPUT_CSV}")

    # Summary report
    successful_count = len(df_results)
    if successful_count > 0:
        mean_rel = df_results["relevance"].mean()
        mean_grd = df_results["groundedness"].mean()
        mean_hlp = df_results["helpfulness"].mean()
        mean_ton = df_results["professional_tone"].mean()
        mean_sft = df_results["safety"].mean()
        mean_ovr = df_results["overall_score"].mean()

        summary_content = f"""======================================================================
LLM-AS-JUDGE EVALUATION SUMMARY (Model: {model_name})
======================================================================
Sample Size Evaluated:     {total_target}
Successfully Judged:       {successful_count}
Failed / Unjudged:         {failed_count}

Average Scores (1-5 Scale):
  Relevance:               {mean_rel:.2f}
  Groundedness:            {mean_grd:.2f}
  Helpfulness:             {mean_hlp:.2f}
  Professional Tone:       {mean_ton:.2f}
  Safety / Non-Fabrication:{mean_sft:.2f}
  Overall Arithmetic Mean: {mean_ovr:.2f}
"""
    else:
        summary_content = "LLM judge evaluation unavailable; no examples were successfully judged.\n"

    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write(summary_content)

    print("\n" + "=" * 50)
    print(f"Target examples:      {total_target}")
    print(f"Successfully judged:  {successful_count}")
    print(f"Failed/unjudged:      {failed_count}")
    if successful_count < total_target:
        print("Status:               LLM judge evaluation is incomplete.")
    print("=" * 50)


if __name__ == "__main__":
    run_llm_judge()
