import os
import sys
import json
import time
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "evaluation" / "results"
PREDS_PATH = RESULTS_DIR / "agent_predictions.csv"
OUTPUT_CSV = RESULTS_DIR / "llm_judge_results.csv"

SAMPLE_SIZE = 30
RANDOM_SEED = 42
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 5


def load_sample():
    if not PREDS_PATH.exists():
        raise FileNotFoundError(f"Missing predictions file: {PREDS_PATH}. Run evaluate_agent.py first.")

    df = pd.read_csv(PREDS_PATH)
    # Fixed reproducible sample of 30 examples
    sample_df = df.sample(n=min(SAMPLE_SIZE, len(df)), random_state=RANDOM_SEED)
    return sample_df


def run_llm_judge():
    print("=" * 70)
    print("LLM-AS-JUDGE EVALUATION HARNESS")
    print("=" * 70)

    sample_df = load_sample()
    print(f"Sample size: {len(sample_df)} examples (seed={RANDOM_SEED})")

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("\n[NOTICE]: Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set in the environment.")
        print("In accordance with evaluation integrity rules, NO scores will be fabricated.")
        print("Creating placeholder structure with 0 completed judge evaluations.")

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
        print(f"Saved empty/unjudged result file: {OUTPUT_CSV}")
        return

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"\n[NOTICE]: Could not initialize Google GenAI client: {e}")
        print("Saving 0 evaluated records without fabricating values.")
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
        return

    judged_records = []
    model_name = "gemini-2.5-flash"

    for idx, (_, row) in enumerate(sample_df.iterrows(), 1):
        tweet_id = row["customer_tweet_id"]
        customer_msg = row["customer_message"]
        predicted_intent = row["predicted_intent"]
        draft_reply = row["draft_reply"]
        decision = row["decision"]

        # Parse historical match if available (Never pass gold_intent or human ratings)
        hist_cust = ""
        hist_supp = ""
        if pd.notna(row.get("historical_match")):
            try:
                h_data = json.loads(row["historical_match"])
                hist_cust = h_data.get("customer_message", "")
                hist_supp = h_data.get("support_response", "")
            except Exception:
                pass

        prompt = f"""You are an expert customer support quality auditor.
Evaluate the following AI support agent draft reply on a scale from 1 (poor) to 5 (excellent) across 5 criteria:

1. Relevance: Does the draft reply directly address the customer's stated issue?
2. Groundedness: Is the response grounded in the historical resolution pattern without hallucinations?
3. Helpfulness: Does it provide actionable, clear next steps for the customer?
4. Professional tone: Is the language polite, empathetic, and professional?
5. Safety: Does it avoid making false refund guarantees, invented policies, or unverified claims?

Customer Message:
"{customer_msg}"

Predicted Intent:
{predicted_intent}

Retrieved Historical Case:
- Customer: "{hist_cust}"
- Resolution: "{hist_supp}"

Draft Reply:
"{draft_reply}"

Agent Routing Decision:
{decision}

Return ONLY valid JSON matching this schema:
{{
  "relevance": <1-5>,
  "groundedness": <1-5>,
  "helpfulness": <1-5>,
  "professional_tone": <1-5>,
  "safety": <1-5>,
  "overall_score": <1.0-5.0 average>,
  "judge_comment": "<concise rationale>"
}}
"""
        success = False
        backoff = INITIAL_BACKOFF_SECONDS

        for attempt in range(MAX_RETRIES):
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                text = resp.text.strip()
                text = text.replace("```json", "").replace("```", "").strip()
                data = json.loads(text)

                judged_records.append({
                    "customer_tweet_id": tweet_id,
                    "relevance": data.get("relevance"),
                    "groundedness": data.get("groundedness"),
                    "helpfulness": data.get("helpfulness"),
                    "professional_tone": data.get("professional_tone"),
                    "safety": data.get("safety"),
                    "overall_score": data.get("overall_score"),
                    "judge_comment": data.get("judge_comment")
                })
                print(f"[{idx}/{len(sample_df)}] Judged tweet_id {tweet_id} -> Overall: {data.get('overall_score')}")
                success = True
                time.sleep(2)  # Mild pacing
                break
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    print(f"[{idx}/{len(sample_df)}] Quota limit encountered on attempt {attempt+1}. Backing off {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    print(f"[{idx}/{len(sample_df)}] API error on attempt {attempt+1}: {e}")
                    time.sleep(backoff)

        if not success:
            print(f"\n[QUOTA / API HALT]: Unable to complete judge evaluations for remaining rows.")
            print(f"Successfully judged {len(judged_records)} of {len(sample_df)} examples.")
            break

    df_out = pd.DataFrame(judged_records)
    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved completed evaluations ({len(df_out)}/{len(sample_df)}) to: {OUTPUT_CSV}")


if __name__ == "__main__":
    run_llm_judge()
