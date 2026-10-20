-- name: revenue_by_month
SELECT substr(sale_date, 1, 7) AS month,
       ROUND(SUM(revenue), 2)  AS revenue,
       SUM(quantity)           AS units
FROM fact_sales
GROUP BY month
ORDER BY month;

-- name: revenue_by_city
SELECT s.city,
       ROUND(SUM(f.revenue), 2) AS revenue,
       COUNT(*)                 AS nb_sales
FROM fact_sales f
JOIN dim_store s ON s.store_id = f.store_id
GROUP BY s.city
ORDER BY revenue DESC;

-- name: top_products
SELECT p.product_name,
       p.category,
       ROUND(SUM(f.revenue), 2) AS revenue,
       SUM(f.quantity)          AS units
FROM fact_sales f
JOIN dim_product p ON p.product_id = f.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10;

-- name: revenue_by_category
SELECT p.category,
       ROUND(SUM(f.revenue), 2)                         AS revenue,
       ROUND(100.0 * SUM(f.revenue) /
             (SELECT SUM(revenue) FROM fact_sales), 1)  AS share_pct
FROM fact_sales f
JOIN dim_product p ON p.product_id = f.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- name: monthly_growth
WITH m AS (
    SELECT substr(sale_date, 1, 7) AS month, SUM(revenue) AS revenue
    FROM fact_sales
    GROUP BY month
)
SELECT month,
       ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / LAG(revenue) OVER (ORDER BY month), 1) AS growth_pct
FROM m
ORDER BY month;
