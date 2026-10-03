# Prompt Pack: flagged-category stakeholder update

The same prompt text lives in `prompt_pack.py` (`PROMPT_TEMPLATE`), and `draft_message()` there is the
**offline, deterministic** fill used by Part 4. No API key or LLM is needed.

## Trigger
Run this prompt when a category's `is_flagged(mom_pct)` result (Part 2) is `"flagged"`.
It does **not** run for `"not_flagged"`, and it never runs for `"escalate_exact_boundary"`
(that case is held for a human decision and logged in `escalated_categories`).

## Input list
| Placeholder | Source | Example |
|---|---|---|
| `{category}` | Part 1 `monthly_category_revenue.csv` | Ethnic Wear |
| `{previous_revenue}` | Part 1, previous month's revenue | 104520.77 |
| `{current_revenue}` | Part 1, current month's revenue | 185107.61 |
| `{mom_pct}` | Part 2 `mom_growth()` | 77.1 |
| `{month}` | the month being reported | May |
| `{prev_month}` | the prior month, named explicitly | April |

## Prompt
```text
You are drafting a short stakeholder update for a Meesho regional manager.
Category: {category}. Period: {month} compared with {prev_month}.
Verified numbers (use ONLY these): previous revenue INR {previous_revenue} in {prev_month}; current revenue INR {current_revenue} in {month}; month-on-month change {mom_pct}%.
Write exactly three labelled parts: Context, Insight, Implication.
- Context: what is measured and over which months.
- Insight: state the change as a FACT using the verified numbers only.
- Implication: one specific, actionable next step; label any proposed cause as a HYPOTHESIS.
Rules: never state a number that is not one of the verified numbers above; never name a reseller (use aliases only); keep it under 120 words; plain language, no jargon.
```

## Checklist (run on every draft before it is used)
1. **Number trace:** every number in the draft equals one of `{previous_revenue}`, `{current_revenue}`, `{mom_pct}` exactly (automated in `numbers_trace()`).
2. **Fact vs hypothesis:** the Insight is labelled *fact*; any proposed cause is labelled *hypothesis*.
3. **Specific next step:** the Implication names what to check or do (who, what), not "look into it".
4. **Correct names and periods:** category, `{month}` and `{prev_month}` appear and match the inputs.
5. **Direction matches the sign:** "rose" only for a positive `{mom_pct}`, "fell" only for a negative one.
6. **No raw reseller names:** resellers appear only as `alias_for(reseller_id)` plus region (`assert_no_raw_names_leak` returns True).
7. **Human approval:** the draft is held as `pending_human_review`; it is never auto-sent.
