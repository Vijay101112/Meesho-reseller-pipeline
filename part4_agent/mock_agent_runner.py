"""Part 4: mock monitoring agent (offline; drafts and holds, never sends).

Uses Part 2's growth_engine and Part 3's prompt_pack unmodified (imported, not re-implemented).
Usage:  python mock_agent_runner.py              # runs the 3 acceptance scenarios
        python mock_agent_runner.py MONTH PREV_CSV CUR_CSV
"""
import calendar
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "part2_engine"))
sys.path.insert(0, os.path.join(ROOT, "part3_narrative"))

from growth_engine import is_flagged, mom_growth, validate_feed  # noqa: E402
from prompt_pack import draft_message  # noqa: E402

MONTHS = list(calendar.month_name)[1:]
MAX_DRAFTS = 3  # cap to prevent notification flooding


def _prev_month(month: str) -> str:
    return MONTHS[MONTHS.index(month) - 1]


def _load_month(path: str, month: str) -> dict:
    with open(path, newline="", encoding="utf-8") as f:
        return {r["category"].strip(): float(r["revenue"]) for r in csv.DictReader(f)
                if r["month"].strip() == month}


def _result(month, valid, errors, flagged=None, suppressed=None, escalated=None):
    return {
        "run_month": month,
        "validation_status": "valid" if valid else "invalid",
        "validation_errors": errors,
        "flagged_categories": flagged or [],
        "suppressed_categories": suppressed or [],
        "escalated_categories": escalated or [],
        "action_taken": "drafted_and_held_for_approval" if valid else "hard_stop",
    }


def run(month: str, previous_month_csv: str, current_month_csv: str) -> dict:
    prev_month = _prev_month(month)

    # (1) load feeds and validate (input guardrail)
    errors = []
    paths = [previous_month_csv] if previous_month_csv == current_month_csv \
        else [previous_month_csv, current_month_csv]
    for p in paths:
        ok, errs = validate_feed(p)
        errors.extend(errs)
    # (2) invalid -> Hard Stop, surface the errors, no MoM attempted
    if errors:
        return _result(month, False, errors)

    prev_rev = _load_month(previous_month_csv, prev_month)
    cur_rev = _load_month(current_month_csv, month)
    for m, data, p in [(prev_month, prev_rev, previous_month_csv), (month, cur_rev, current_month_csv)]:
        if not data:
            return _result(month, False, [f"no rows for month={m} in {os.path.basename(p)}"])
    missing = [c for c in cur_rev if c not in prev_rev]
    if missing:
        return _result(month, False, [f"no previous-month revenue for category={c}" for c in missing])

    # (3) MoM for every category, (4) is_flagged for every category
    rows, escalated = [], []
    for category, current in cur_rev.items():
        previous = prev_rev[category]
        pct = mom_growth(previous, current)
        status = is_flagged(pct)
        if status == "flagged":
            rows.append((category, pct, previous, current))
        elif status == "escalate_exact_boundary":
            escalated.append(category)  # (7b) held for a human; never dropped, never drafted

    # (5) sort flagged by magnitude (ties broken by name for determinism)
    rows.sort(key=lambda r: (-abs(r[1]), r[0]))

    # (6) draft for at most the top 3; (7) log the rest as suppressed
    flagged_out, suppressed = [], []
    for i, (category, pct, previous, current) in enumerate(rows):
        if i < MAX_DRAFTS:
            flagged_out.append({
                "category": category, "mom_pct": pct,
                "previous_revenue": previous, "current_revenue": current,
                "drafted": True,
                "message": draft_message(category, previous, current, pct, month, prev_month),
                "approval_status": "pending_human_review",  # feedback loop: never auto-sent
            })
        else:
            suppressed.append(category)  # suppressed, review manually

    # (8) one structured JSON-able object per run
    return _result(month, True, [], flagged_out, suppressed, escalated)


SCENARIOS = [
    ("May", "part2_engine/fixtures/monthly_category_revenue.csv", "part2_engine/fixtures/monthly_category_revenue.csv", "scenario_may.json"),
    ("June", "part2_engine/fixtures/monthly_category_revenue.csv", "part2_engine/fixtures/monthly_category_revenue.csv", "scenario_june.json"),
    ("July", "part2_engine/fixtures/monthly_category_revenue.csv", "part2_engine/fixtures/corrupted_feed.csv", "scenario_corrupted.json"),
]


def main(argv):
    if len(argv) == 4:
        print(json.dumps(run(argv[1], argv[2], argv[3]), indent=2))
        return
    out_dir = os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    for month, prev, cur, fname in SCENARIOS:
        result = run(month, os.path.join(ROOT, prev), os.path.join(ROOT, cur))
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        drafted = [e["category"] for e in result["flagged_categories"]]
        print(f"[{month}] {result['validation_status']} / {result['action_taken']} | drafted={drafted} "
              f"suppressed={result['suppressed_categories']} -> output/{fname}")


if __name__ == "__main__":
    main(sys.argv)
