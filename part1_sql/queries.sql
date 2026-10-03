-- Part 1: standing business queries for the Meesho reseller dataset (SQLite).
-- Each block starts with "-- name: <output_file_stem>"; run_queries.py executes
-- every block and writes part1_sql/output/<name>.csv.
-- NOTE: revenue is SUM(quantity * unit_price) over ALL order statuses
-- (Delivered, Returned, Cancelled, Pending), exactly as the brief specifies.

-- name: monthly_category_revenue
SELECT month,
       category,
       ROUND(SUM(quantity * unit_price), 2) AS revenue,
       COUNT(*)                             AS n_orders
FROM orders
GROUP BY month, category
ORDER BY CASE month WHEN 'April' THEN 1 WHEN 'May' THEN 2 WHEN 'June' THEN 3 END,
         CASE category WHEN 'Ethnic Wear' THEN 1 WHEN 'Western Wear' THEN 2
                       WHEN 'Kids Wear' THEN 3 WHEN 'Home & Kitchen' THEN 4
                       ELSE 5 END;

-- name: region_revenue
SELECT r.region,
       ROUND(SUM(o.quantity * o.unit_price), 2) AS total_revenue,
       COUNT(*)                                 AS n_orders
FROM orders o
JOIN resellers r ON r.reseller_id = o.reseller_id
GROUP BY r.region
ORDER BY total_revenue DESC;

-- name: top_resellers
SELECT r.reseller_id,
       r.reseller_name,
       r.region,
       ROUND(SUM(o.quantity * o.unit_price), 2) AS total_spend
FROM orders o
JOIN resellers r ON r.reseller_id = o.reseller_id
GROUP BY r.reseller_id
HAVING SUM(o.quantity * o.unit_price) > 50000
ORDER BY total_spend DESC
LIMIT 5;

-- name: zero_order_resellers
-- LEFT JOIN keeps every reseller; an unmatched reseller gets NULL in o.order_id.
SELECT r.reseller_id, r.reseller_name, r.region
FROM resellers r
LEFT JOIN orders o ON o.reseller_id = r.reseller_id
WHERE o.order_id IS NULL;

-- name: zero_order_count_demo
-- WHY COUNT(*) CANNOT DETECT "no orders": for an unmatched reseller the LEFT JOIN
-- still emits ONE row (all order columns NULL), so COUNT(*) = 1. COUNT(order_id)
-- skips NULLs, so it correctly returns 0. Use COUNT(order_id) (or WHERE
-- order_id IS NULL) to test for zero matches, never COUNT(*).
SELECT r.reseller_id,
       COUNT(*)          AS count_star,
       COUNT(o.order_id) AS count_order_id
FROM resellers r
LEFT JOIN orders o ON o.reseller_id = r.reseller_id
WHERE r.reseller_id = 'RS024'
GROUP BY r.reseller_id;

-- name: june_delivered_aov
SELECT ROUND(SUM(quantity * unit_price) / COUNT(*), 2) AS aov_june_delivered
FROM orders
WHERE month = 'June' AND status = 'Delivered';

-- name: grand_total_and_month_totals
-- Support query: cross-checks (grand total, per-month totals) used in Part 3.
SELECT month,
       ROUND(SUM(quantity * unit_price), 2) AS total_revenue,
       COUNT(*)                             AS n_orders
FROM orders
GROUP BY month
ORDER BY CASE month WHEN 'April' THEN 1 WHEN 'May' THEN 2 ELSE 3 END;
