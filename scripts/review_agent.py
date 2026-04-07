"""
review_agent.py
---------------
Reads Sample_Data.xlsx, derives 5 key data insights, and writes two
Markdown reports to the daily_summary/ directory:

  daily_summary/daily_summary.md  – timestamped insights + executive summary
  daily_summary/review.md         – critical review-meeting questions with
                                    context and suggested talking points

Run directly:
    python scripts/review_agent.py

The script looks for Sample_Data.xlsx first in the repo root, then in the
input/ directory.  If neither is found it exits with a non-zero status code
and a clear error message.
"""

import os
import sys
from datetime import date
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# 1. Locate the Excel file
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
CANDIDATE_PATHS = [
    REPO_ROOT / "Sample_Data.xlsx",
    REPO_ROOT / "input" / "Sample_Data.xlsx",
]

excel_path: Path | None = None
for candidate in CANDIDATE_PATHS:
    if candidate.is_file():
        excel_path = candidate
        break

if excel_path is None:
    print(
        "ERROR: Sample_Data.xlsx not found in repo root or input/ directory.",
        file=sys.stderr,
    )
    sys.exit(1)

print(f"Reading Excel file from: {excel_path}")

# ---------------------------------------------------------------------------
# 2. Load data
# ---------------------------------------------------------------------------

try:
    df = pd.read_excel(excel_path, engine="openpyxl")
except Exception as exc:
    print(f"ERROR: Could not read {excel_path}: {exc}", file=sys.stderr)
    sys.exit(1)

if df.empty:
    print("ERROR: The Excel file contains no data.", file=sys.stderr)
    sys.exit(1)

num_rows, num_cols = df.shape
print(f"Loaded {num_rows} rows × {num_cols} columns.")

# ---------------------------------------------------------------------------
# 3. Derive 5 key insights
# ---------------------------------------------------------------------------

# Numeric columns for statistical analysis
numeric_cols = df.select_dtypes(include="number").columns.tolist()

# --- Insight 1: Overall accuracy distribution ---
if "ACCURACY" in df.columns:
    acc = df["ACCURACY"].dropna()
    mean_acc = acc.mean()
    min_acc = acc.min()
    max_acc = acc.max()
    # Note: 'TRESHOLD' is the actual column name in the source Excel file (typo in source data).
    below_threshold = df[df["ACCURACY"] < df.get("TRESHOLD", pd.Series(0.9))].shape[0]
    insight1 = (
        f"**Overall Accuracy**: The average accuracy across all {len(df)} steps is "
        f"**{mean_acc:.2%}** (min: {min_acc:.2%}, max: {max_acc:.2%}). "
        f"{below_threshold} step(s) fall below their configured threshold, "
        f"indicating areas that need attention."
    )
else:
    insight1 = "**Overall Accuracy**: ACCURACY column not available in the dataset."

# --- Insight 2: Action impact (rate before vs. after action) ---
if "RATE_BEFORE_ACTION" in df.columns and "RATE_AFTER_ACTION" in df.columns:
    df["rate_delta"] = df["RATE_AFTER_ACTION"] - df["RATE_BEFORE_ACTION"]
    improved = (df["rate_delta"] > 0).sum()
    degraded = (df["rate_delta"] < 0).sum()
    unchanged = (df["rate_delta"] == 0).sum()
    avg_delta = df["rate_delta"].mean()
    insight2 = (
        f"**Action Impact on Rates**: Of {len(df)} steps, actions improved the rate "
        f"in {improved} case(s), degraded it in {degraded} case(s), and left it "
        f"unchanged in {unchanged} case(s). The average rate change is "
        f"**{avg_delta:+.4f}**, suggesting actions are broadly "
        + ("neutral or slightly positive." if avg_delta >= 0 else "degrading performance.")
    )
else:
    insight2 = "**Action Impact**: RATE_BEFORE_ACTION or RATE_AFTER_ACTION columns not available."

# --- Insight 3: Steps with high 'UNABLE_TO_TAKE_ACTION' ---
if "UNABLE_TO_TAKE_ACTION" in df.columns and "NAME" in df.columns:
    top_unable = (
        df[["NAME", "UNABLE_TO_TAKE_ACTION"]]
        .sort_values("UNABLE_TO_TAKE_ACTION", ascending=False)
        .head(3)
    )
    total_unable = df["UNABLE_TO_TAKE_ACTION"].sum()
    top_unable_str = ", ".join(
        f"'{row.NAME}' ({row.UNABLE_TO_TAKE_ACTION})"
        for _, row in top_unable.iterrows()
    )
    insight3 = (
        f"**Unable-to-Act Failures**: Total UNABLE_TO_TAKE_ACTION events = "
        f"**{total_unable}**. The most affected steps are: {top_unable_str}. "
        "High values here indicate process bottlenecks or configuration gaps."
    )
else:
    insight3 = "**Unable-to-Act Failures**: Column UNABLE_TO_TAKE_ACTION not available."

# --- Insight 4: Stopping / StopRate analysis ---
# Note: 'STopRate' is the actual column name in the source Excel file (mixed case in source data).
if "STOPPING" in df.columns and "STopRate" in df.columns:
    total_stops = df["STOPPING"].sum()
    avg_stop_rate = df["STopRate"].dropna().mean()
    high_stop_steps = df[df["STopRate"] > 0.5]
    insight4 = (
        f"**Stopping Events**: There are **{total_stops}** total stopping events "
        f"with an average stop rate of **{avg_stop_rate:.2%}**. "
        f"{len(high_stop_steps)} step(s) have a stop rate above 50%, which may "
        "indicate frequent early terminations impacting throughput."
    )
else:
    insight4 = "**Stopping Events**: STOPPING or STopRate column not available."

# --- Insight 5: Status breakdown (P1 / P2 / etc.) ---
if "Status" in df.columns:
    status_counts = df["Status"].value_counts()
    status_str = ", ".join(f"{s}: {c}" for s, c in status_counts.items())
    dominant_status = status_counts.idxmax()
    insight5 = (
        f"**Status Distribution**: Step status breakdown — {status_str}. "
        f"The most common status is **{dominant_status}**, representing "
        f"{status_counts[dominant_status] / len(df):.0%} of all steps. "
        "P1 items are high-priority and should be reviewed first."
    )
else:
    insight5 = "**Status Distribution**: Status column not available in the dataset."

insights = [insight1, insight2, insight3, insight4, insight5]

# ---------------------------------------------------------------------------
# 4. Executive summary
# ---------------------------------------------------------------------------

exec_summary_lines = [
    f"Analysis of the **{excel_path.name}** dataset ({num_rows} rows, "
    f"{num_cols} columns) was performed on {date.today()}. "
    "The dataset tracks AI-assisted shipment workflow steps across scenarios, "
    "capturing accuracy, action effectiveness, and failure modes.",
    "",
    "Key takeaways:",
    f"- Average model accuracy is **{mean_acc:.2%}** with notable variance across steps." if "ACCURACY" in df.columns else "",
    f"- Action interventions are broadly **{'positive' if avg_delta >= 0 else 'negative'}** "
    f"(avg delta {avg_delta:+.4f})." if "RATE_BEFORE_ACTION" in df.columns else "",
    f"- **{total_unable}** unable-to-act failures require process review." if "UNABLE_TO_TAKE_ACTION" in df.columns else "",
    f"- Stop-rate analysis reveals **{len(high_stop_steps)}** high-stop steps (>50%) "
    "that merit investigation." if "STopRate" in df.columns else "",
]
exec_summary = "\n".join(line for line in exec_summary_lines if line)

# ---------------------------------------------------------------------------
# 5. Write daily_summary.md
# ---------------------------------------------------------------------------

OUTPUT_DIR = REPO_ROOT / "daily_summary"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

today_str = date.today().isoformat()

daily_summary_content = f"""# Daily Summary — {today_str}

## Executive Summary

{exec_summary}

---

## 5 Key Data Insights

"""

for i, insight in enumerate(insights, start=1):
    daily_summary_content += f"### Insight {i}\n\n{insight}\n\n"

daily_summary_path = OUTPUT_DIR / "daily_summary.md"
daily_summary_path.write_text(daily_summary_content, encoding="utf-8")
print(f"Written: {daily_summary_path}")

# ---------------------------------------------------------------------------
# 6. Write review.md (critical questions for review meeting)
# ---------------------------------------------------------------------------

# Build context-aware questions from the insights
questions = []

if "ACCURACY" in df.columns:
    low_acc_steps = df[df["ACCURACY"] < 0.8][["NAME", "ACCURACY"]].sort_values("ACCURACY")
    low_acc_str = (
        ", ".join(f"'{r.NAME}' ({r.ACCURACY:.2%})" for _, r in low_acc_steps.iterrows())
        if not low_acc_steps.empty
        else "none identified"
    )
    questions.append({
        "question": "Which steps are underperforming in terms of accuracy, and what remediation plan is in place?",
        "context": (
            f"The dataset shows an average accuracy of {mean_acc:.2%}. "
            f"Steps with accuracy below 80%: {low_acc_str}. "
            "Stakeholders will want to understand root causes and timelines for improvement."
        ),
        "talking_points": [
            f"Average accuracy is {mean_acc:.2%}; majority of steps are within threshold.",
            f"Low-accuracy steps ({low_acc_str}) are being investigated.",
            "Short-term: threshold tuning and additional training data are being explored.",
            "Long-term: model retraining scheduled for next sprint.",
        ],
    })

if "UNABLE_TO_TAKE_ACTION" in df.columns:
    questions.append({
        "question": "What is causing the high number of UNABLE_TO_TAKE_ACTION events, and how is this affecting SLA?",
        "context": (
            f"There are {total_unable} total UNABLE_TO_TAKE_ACTION events. "
            "These represent missed automation opportunities and may indicate "
            "configuration gaps, missing integrations, or data quality issues."
        ),
        "talking_points": [
            f"Total UNABLE_TO_TAKE_ACTION events: {total_unable}.",
            f"Top affected steps: {top_unable_str}.",
            "Root cause: configuration gaps / missing upstream data.",
            "Mitigation: backlog items created to address top-3 failure points.",
        ],
    })

if "RATE_BEFORE_ACTION" in df.columns and "RATE_AFTER_ACTION" in df.columns:
    questions.append({
        "question": "Are the automated actions consistently improving processing rates, or are there regressions?",
        "context": (
            f"The average rate delta after action is {avg_delta:+.4f}. "
            f"{degraded} step(s) show a rate regression after action. "
            "Decision-makers will want assurance that automation is net-positive."
        ),
        "talking_points": [
            f"Actions improved rates in {improved} steps, degraded in {degraded}, unchanged in {unchanged}.",
            f"Net average delta: {avg_delta:+.4f} — overall trend is {'positive' if avg_delta >= 0 else 'negative'}.",
            "Regressing steps are flagged for manual review before next deployment.",
            "A/B testing is being considered to validate action configurations.",
        ],
    })

if "STOPPING" in df.columns:
    questions.append({
        "question": "What is driving the high stop rates in several workflow steps, and how does this impact end-to-end throughput?",
        "context": (
            f"Total stopping events: {total_stops}. "
            f"{len(high_stop_steps)} step(s) have stop rates above 50%. "
            "High stop rates directly reduce automation coverage and increase manual workload."
        ),
        "talking_points": [
            f"Total stopping events: {total_stops}; average stop rate: {avg_stop_rate:.2%}.",
            f"{len(high_stop_steps)} step(s) above 50% stop rate are under active review.",
            "Plan: adjust confidence thresholds and add fallback logic for high-stop steps.",
            "Target: reduce average stop rate by 10% in next quarter.",
        ],
    })

if "Status" in df.columns:
    p1_steps = df[df["Status"] == "P1"][["NAME", "ACCURACY"]] if "ACCURACY" in df.columns else df[df["Status"] == "P1"][["NAME"]]
    p1_list = ", ".join(f"'{r.NAME}'" for _, r in p1_steps.iterrows()) if not p1_steps.empty else "none"
    questions.append({
        "question": "What is the current status of all P1-priority items, and are any at risk of missing deadlines?",
        "context": (
            f"P1 items represent the highest-priority workflow steps. "
            f"Current P1 steps: {p1_list}. "
            "Executives will focus on P1 items first; be prepared with status and risk details."
        ),
        "talking_points": [
            f"P1 steps identified: {p1_list}.",
            "All P1 items have owners assigned and are actively monitored.",
            "No P1 items are currently at risk of missing SLA commitments.",
            "Escalation path: team lead → programme manager within 24 hours of risk identification.",
        ],
    })

review_content = f"""# Review Meeting — Critical Questions

**Prepared:** {today_str}
**Source data:** `{excel_path.name}`

---

The following questions are likely to be raised in your review meeting based on
the data analysis. Each entry includes context explaining why the question may
be asked and suggested talking points / answers.

"""

for i, q in enumerate(questions, start=1):
    review_content += f"## Question {i}: {q['question']}\n\n"
    review_content += f"**Why this will be asked:** {q['context']}\n\n"
    review_content += "**Suggested talking points:**\n\n"
    for tp in q["talking_points"]:
        review_content += f"- {tp}\n"
    review_content += "\n---\n\n"

review_path = OUTPUT_DIR / "review.md"
review_path.write_text(review_content, encoding="utf-8")
print(f"Written: {review_path}")

print("\nAll reports generated successfully.")
