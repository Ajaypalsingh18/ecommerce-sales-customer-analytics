/* ============================================================
   E-Commerce Sales Analytics — SQL Analysis
   Tables: customers, products, orders, order_items
   Engine: SQLite (syntax is standard ANSI SQL; portable to
   MySQL/PostgreSQL with minor date-function tweaks)
   ============================================================ */


-- 1. MONTHLY REVENUE TREND (Delivered orders only)
-- ------------------------------------------------------------
SELECT
    strftime('%Y-%m', order_date)          AS order_month,
    COUNT(DISTINCT order_id)                AS total_orders,
    ROUND(SUM(order_total), 2)              AS revenue,
    ROUND(AVG(order_total), 2)              AS avg_order_value
FROM orders
WHERE status = 'Delivered'
GROUP BY order_month
ORDER BY order_month;


-- 2. TOP 10 PRODUCTS BY REVENUE (JOIN + GROUP BY)
-- ------------------------------------------------------------
SELECT
    p.product_name,
    p.category,
    SUM(oi.quantity)                        AS units_sold,
    ROUND(SUM(oi.line_total), 2)            AS total_revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders   o ON o.order_id   = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY p.product_id
ORDER BY total_revenue DESC
LIMIT 10;


-- 3. REVENUE & AOV BY CATEGORY
-- ------------------------------------------------------------
SELECT
    p.category,
    ROUND(SUM(oi.line_total), 2)            AS revenue,
    COUNT(DISTINCT oi.order_id)             AS orders,
    ROUND(SUM(oi.line_total) * 1.0 / COUNT(DISTINCT oi.order_id), 2) AS avg_order_value
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders   o ON o.order_id   = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY p.category
ORDER BY revenue DESC;


-- 4. CUSTOMER LIFETIME VALUE (CTE) + SEGMENT
-- ------------------------------------------------------------
WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.first_name || ' ' || c.last_name  AS customer_name,
        c.segment,
        c.city,
        COUNT(DISTINCT o.order_id)          AS total_orders,
        ROUND(SUM(o.order_total), 2)        AS lifetime_value
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id
)
SELECT *
FROM customer_revenue
ORDER BY lifetime_value DESC
LIMIT 20;


-- 5. TOP 20% OF CUSTOMERS' SHARE OF REVENUE (Pareto / 80-20 check)
-- Uses a CTE + window function to rank customers, then a subquery
-- to isolate the top quintile and compare against total revenue.
-- ------------------------------------------------------------
WITH customer_revenue AS (
    SELECT
        c.customer_id,
        ROUND(SUM(o.order_total), 2) AS lifetime_value
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id
),
ranked AS (
    SELECT
        customer_id,
        lifetime_value,
        NTILE(5) OVER (ORDER BY lifetime_value DESC) AS quintile
    FROM customer_revenue
)
SELECT
    (SELECT ROUND(SUM(lifetime_value), 2) FROM ranked WHERE quintile = 1) AS top20pct_revenue,
    (SELECT ROUND(SUM(lifetime_value), 2) FROM customer_revenue)          AS total_revenue,
    ROUND(
        100.0 * (SELECT SUM(lifetime_value) FROM ranked WHERE quintile = 1)
        / (SELECT SUM(lifetime_value) FROM customer_revenue), 1
    ) AS top20pct_share_of_revenue;


-- 6. MONTH-OVER-MONTH REVENUE GROWTH (Window function: LAG)
-- ------------------------------------------------------------
WITH monthly AS (
    SELECT
        strftime('%Y-%m', order_date) AS order_month,
        ROUND(SUM(order_total), 2)    AS revenue
    FROM orders
    WHERE status = 'Delivered'
    GROUP BY order_month
)
SELECT
    order_month,
    revenue,
    LAG(revenue) OVER (ORDER BY order_month)          AS prev_month_revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY order_month))
        / LAG(revenue) OVER (ORDER BY order_month), 1
    ) AS mom_growth_pct
FROM monthly
ORDER BY order_month;


-- 7. ORDER CANCELLATION / RETURN RATE BY CITY (subquery in SELECT)
-- ------------------------------------------------------------
SELECT
    c.city,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN o.status IN ('Cancelled','Returned') THEN 1 ELSE 0 END) AS cancelled_or_returned,
    ROUND(
        100.0 * SUM(CASE WHEN o.status IN ('Cancelled','Returned') THEN 1 ELSE 0 END)
        / COUNT(*), 1
    ) AS cancel_return_rate_pct
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.city
ORDER BY cancel_return_rate_pct DESC;


-- 8. REPEAT PURCHASE RATE (customers with 2+ orders / total customers who ordered)
-- ------------------------------------------------------------
WITH order_counts AS (
    SELECT customer_id, COUNT(*) AS n_orders
    FROM orders
    WHERE status = 'Delivered'
    GROUP BY customer_id
)
SELECT
    COUNT(*)                                             AS customers_who_ordered,
    SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END)        AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS repeat_rate_pct
FROM order_counts;


-- 9. PAYMENT METHOD PREFERENCE BY REGION
-- ------------------------------------------------------------
SELECT
    c.region,
    o.payment_method,
    COUNT(*) AS order_count
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.region, o.payment_method
ORDER BY c.region, order_count DESC;


-- 10. BEST-SELLING CATEGORY PER MONTH (window function: RANK)
-- ------------------------------------------------------------
WITH monthly_category AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS order_month,
        p.category,
        SUM(oi.line_total) AS revenue,
        RANK() OVER (
            PARTITION BY strftime('%Y-%m', o.order_date)
            ORDER BY SUM(oi.line_total) DESC
        ) AS category_rank
    FROM order_items oi
    JOIN orders o   ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.status = 'Delivered'
    GROUP BY order_month, p.category
)
SELECT order_month, category, ROUND(revenue, 2) AS revenue
FROM monthly_category
WHERE category_rank = 1
ORDER BY order_month;
