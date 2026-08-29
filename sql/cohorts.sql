

-- Cohort Retention Analysis

WITH first_purchases AS (
    SELECT 
        customer_unique_id,
        DATEFROMPARTS(YEAR(MIN(order_purchase_timestamp)),
                      MONTH(MIN(order_purchase_timestamp)), 1) AS first_purchase_month
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE order_status = 'delivered'
    GROUP BY customer_unique_id
),

monthly_purchases AS (
    SELECT 
        c.customer_unique_id,
        DATEFROMPARTS(YEAR(order_purchase_timestamp),
                      MONTH(order_purchase_timestamp), 1) AS purchase_month
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE order_status = 'delivered'
    GROUP BY c.customer_unique_id,
             DATEFROMPARTS(YEAR(order_purchase_timestamp),
                           MONTH(order_purchase_timestamp), 1)
),

cohort_data AS (
    SELECT 
        f.first_purchase_month,
        m.purchase_month,
        DATEDIFF(MONTH, f.first_purchase_month, m.purchase_month) AS month_number,
        COUNT(DISTINCT f.customer_unique_id) AS active_customers
    FROM first_purchases f
    JOIN monthly_purchases m ON f.customer_unique_id = m.customer_unique_id
    GROUP BY f.first_purchase_month, m.purchase_month,
             DATEDIFF(MONTH, f.first_purchase_month, m.purchase_month)
),

cohort_size AS (
    SELECT first_purchase_month, active_customers AS cohort_total
    FROM cohort_data
    WHERE month_number = 0
)

SELECT 
    d.first_purchase_month,
    d.month_number,
    d.active_customers,
    s.cohort_total,
    ROUND(CAST(d.active_customers AS DECIMAL(18,4)) / s.cohort_total * 100, 2) AS retention_percent
FROM cohort_data d
JOIN cohort_size s ON d.first_purchase_month = s.first_purchase_month
ORDER BY d.first_purchase_month, d.month_number;