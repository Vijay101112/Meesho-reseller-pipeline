# Meesho Reseller Growth & Alert Intelligence Pipeline

An end-to-end, fully offline pipeline: **SQL numbers -> Python rule engine -> templated narrative -> guarded, human-reviewed agent run.**
Requires only Python 3.9+ and the standard library. **No API keys, accounts or network access are used anywhere; the whole pipeline runs with zero API keys set.**

## Quick start (everything, in order)
```bash
python run_pipeline.py
```
This regenerates the data, runs all SQL, runs every test, and runs the three agent scenarios. Or run each stage yourself:

| Stage | Command (from repo root) |
|---|---|
| Regenerate dataset (seed 42, do not edit) | `python data/generate_dataset.py` |
| Part 1: SQL queries -> `part1_sql/output/*.csv` | `python part1_sql/run_queries.py` |
| Part 2: engine tests | `cd part2_engine && python -m unittest -v` |
| Part 3: masking + template tests | `cd part3_narrative && python -m unittest -v` |
| Part 4: agent tests | `cd part4_agent && python -m unittest -v` |
| Part 4: run May, June and corrupted-feed scenarios | `python part4_agent/mock_agent_runner.py` (writes `part4_agent/output/scenario_*.json`) |
| Part 4: single custom run | `python part4_agent/mock_agent_runner.py May <prev.csv> <cur.csv>` |

## How the Parts connect
1. `data/generate_dataset.py` creates `resellers.csv`, `orders.csv` and `meesho_reseller.db`.
2. **Part 1** (`queries.sql` + `run_queries.py`) writes `part1_sql/output/monthly_category_revenue.csv`.
3. That file is copied to `part2_engine/fixtures/` and is the input to **Part 2** (`growth_engine.py`: `mom_growth`, `is_flagged`, `validate_feed`).
4. **Part 3** (`prompt_pack.md`, `prompt_pack.py`, `masking.py`, `narrative_report.md`) turns verified numbers into narratives.
5. **Part 4** (`mock_agent_runner.py`) imports Part 2's functions and Part 3's `draft_message` unmodified and reads the Part 1 feed to produce one JSON object per run.

## Repository layout
```
data/            generate_dataset.py, resellers.csv, orders.csv, meesho_reseller.db
part1_sql/       queries.sql, run_queries.py, output/*.csv, output/README.md
part2_engine/    growth_engine.py, test_growth_engine.py, fixtures/*.csv
part3_narrative/ prompt_pack.md, prompt_pack.py, narrative_report.md, masking.py, test_masking.py
part4_agent/     agent_spec.md, mock_agent_runner.py, test_mock_agent_runner.py, output/*.json
run_pipeline.py  README.md
```

## Mapping each Part to its workflow pattern
- **Part 1 -> Part 2:** compute real numbers via SQL first, then hand off to a rule engine. The "significant change" rule (`abs(MoM) > 8%`, exact boundary escalated) is explicit and testable rather than a judgement call.
- **Part 2:** an input guardrail (`validate_feed`) plus Given-When-Then tests, so bad data stops the workflow instead of producing a wrong report.
- **Part 3:** Context -> Insight -> Implication narrative with fact/hypothesis labels, a validation checklist, and a masking policy for external text.
- **Part 4:** mirrors an Intake -> Summary -> Report Draft -> Validate flow: validate the feed, compute and flag, draft (capped at 3), then hold every draft for human approval. Nothing is ever sent.

## Notes and caveats
- Revenue is `SUM(quantity * unit_price)` over all order statuses, as the brief specifies. Returned and cancelled orders are therefore included; only the June AOV is restricted to Delivered.
- `flagged_categories` in the JSON lists the drafted (top 3) categories; flagged categories over the cap are listed only in `suppressed_categories`, matching the brief's acceptance criteria.
- `mom_growth` raises `ValueError` when the previous value is 0 (growth is undefined).
- `part1_sql/output/README.md` is internal (it contains raw reseller names); externally shared text goes through `masking.py`.

## Documentation referenced
Python standard-library docs only: `sqlite3`, `csv`, `json`, `unittest`, `re`, `calendar`, `tempfile`, `subprocess`.

## Author
vijayalakshmi C
