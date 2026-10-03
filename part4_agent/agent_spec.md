# Agent Specification: Reseller Growth & Alert Monitor

## 4.1 Five core components

**Goal.** Keep Meesho category managers informed of any category whose month-on-month revenue moves beyond the 8% threshold, with a human approving every message before it goes out.

**Tools.**
- `validate_feed(csv_path)` (Part 2): input guardrail.
- `mom_growth(previous, current)` (Part 2): MoM percentage.
- `is_flagged(mom_pct, threshold=8.0)` (Part 2): `flagged` / `not_flagged` / `escalate_exact_boundary`.
- `draft_message(...)` (Part 3 `prompt_pack.py`): offline template-fill of the prompt pack (Context, Insight, Implication).

**Memory / State.** Between runs the agent needs the previous month's revenue per category. In this project that state is the Part 1 feed (`monthly_category_revenue.csv`), read at the start of each run. Nothing else is remembered; each run's JSON is the audit record.

**Planner.** The ordered subtasks in section 4.2.

**Feedback loop.** Every drafted message is marked `approval_status: "pending_human_review"` and the run's `action_taken` is `drafted_and_held_for_approval`. This is a simulated flag only: no email, Slack or SMTP integration exists, and nothing is ever sent automatically. A human reads, edits or rejects each draft.

## Guardrails
- **Input:** `validate_feed` must pass on both the previous-month and current-month feeds before anything else runs.
- **Action:** no message is ever auto-sent; messages are only drafted and held. At most 3 are drafted per run (anti-flooding cap).
- **Output:** every number in a drafted message must trace to a Part 1 / Part 2 value (previous revenue, current revenue, `mom_pct`). `draft_message` raises if an untraceable number appears. Resellers, if mentioned, appear only as `alias_for(id)` (Part 3 masking).

## Stopping conditions
- **Success:** drafts are produced (or correctly zero drafts if nothing crossed the threshold), with every number traceable. A zero-flag run still reports `action_taken = "drafted_and_held_for_approval"` with an empty `flagged_categories`, because the schema allows only two action values.
- **Error:** `validate_feed` returns False. The run is a **Hard Stop**: `validation_status = "invalid"`, `action_taken = "hard_stop"`, the validation errors are surfaced, and no MoM computation is attempted. Missing months or categories are treated the same way. It is never a silent skip.

## 4.2 Ordered subtasks (the Planner)
1. Load the monthly revenue feed(s) and run `validate_feed`.
2. If invalid: Hard Stop and report the errors.
3. If valid: compute `mom_growth` for every category against the previous month.
4. Run `is_flagged` on every category.
5. Sort flagged categories by `abs(mom_pct)` descending.
6. Draft a message (via Part 3's template) for at most the top 3 by magnitude. The cap prevents notification flooding.
7. Log any remaining flagged categories beyond the cap as `suppressed_categories` ("suppressed, review manually") with no draft.
   - 7b. Log any category whose result is `escalate_exact_boundary` into `escalated_categories`, with no draft. It is neither flagged nor not_flagged, so it must not be dropped or mistaken for either.
8. Emit one structured JSON object per run.

## 4.3 Output schema
Exactly these top-level keys, in this order:

| Key | Type / values |
|---|---|
| `run_month` | e.g. `"May"` |
| `validation_status` | `"valid"` or `"invalid"` |
| `validation_errors` | list of strings (empty on success) |
| `flagged_categories` | list of objects: `category`, `mom_pct`, `previous_revenue`, `current_revenue`, `drafted` (bool), `message` (when drafted), plus `approval_status` |
| `suppressed_categories` | list of category names (flagged but over the cap) |
| `escalated_categories` | list of category names at exactly the threshold |
| `action_taken` | `"drafted_and_held_for_approval"` or `"hard_stop"` |

Note: `flagged_categories` lists the categories that were drafted (up to 3); flagged categories beyond the cap appear only in `suppressed_categories`.

## Given-When-Then specs (agent level)
1. **GIVEN** April to May Ethnic Wear revenue moves from 104520.77 to 185107.61, **WHEN** the agent computes `mom_growth` then `is_flagged`, **THEN** `mom_growth` is 77.1 and the result is `"flagged"`, so a draft is held for approval.
2. **GIVEN** May to June Beauty & Personal Care revenue moves from 35542.11 to 37559.07, **WHEN** the agent evaluates it, **THEN** `mom_growth` is 5.67 and the result is `"not_flagged"`, so the category appears in neither `flagged_categories` nor `suppressed_categories`.
3. **GIVEN** a synthetic pair previous=100000, current=108000 (exactly on the boundary), **WHEN** the agent evaluates it, **THEN** `mom_growth` is exactly 8.0 and the result is `"escalate_exact_boundary"`, so it is listed in `escalated_categories` and neither drafted nor dropped.
4. **GIVEN** the corrupted feed fixture, **WHEN** `validate_feed` runs inside the agent, **THEN** it returns `(False, errors)` with exactly 3 errors (negative-revenue row, missing-category row, missing-revenue row, in that order), and the run is a Hard Stop with empty `flagged_categories` and `suppressed_categories`.
