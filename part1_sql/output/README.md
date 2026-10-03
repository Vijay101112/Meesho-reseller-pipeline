# Part 1 notes (internal: contains raw reseller names)

Run: `python part1_sql/run_queries.py` (executes every `-- name:` block in `queries.sql` against `data/meesho_reseller.db`).

| File | Query |
|---|---|
| `monthly_category_revenue.csv` | revenue and order count by month and category (15 rows; input to Parts 2 and 4) |
| `region_revenue.csv` | JOIN, GROUP BY region (North 337125.46, West 333106.33, South 316736.68, East 275098.45; sums to 1262066.92) |
| `top_resellers.csv` | HAVING total_spend > 50000, descending, LIMIT 5 |
| `zero_order_resellers.csv` | LEFT JOIN ... WHERE order_id IS NULL: only RS024 (Ahmedabad Reseller 6, West) |
| `zero_order_count_demo.csv` | RS024 shows `count_star = 1`, `count_order_id = 0` |
| `june_delivered_aov.csv` | AOV for June, Delivered orders: 1267.69 |
| `grand_total_and_month_totals.csv` | support: April 419417.43, May 444594.25, June 398055.24 |

## Why COUNT(*) is the wrong test for a zero-match LEFT JOIN
A LEFT JOIN keeps every reseller. For RS024, which has no orders, it still emits **one** row whose order columns are all NULL.
`COUNT(*)` counts rows, so it returns **1**. `COUNT(order_id)` skips NULLs, so it returns **0**.
Therefore `COUNT(*)` can never detect "no matching orders"; use `COUNT(order_id)` or `WHERE order_id IS NULL`.

Caveat: as specified, revenue includes Returned, Cancelled and Pending orders. Only the AOV query filters on status.
