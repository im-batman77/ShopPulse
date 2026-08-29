

-- RFM Analysis

WITH customer_rfm AS (
    SELECT
        c.customer_unique_id,
        DATEDIFF(
            DAY,
            MAX(o.order_purchase_timestamp),
            (SELECT MAX(order_purchase_timestamp) FROM orders)
        ) AS recency,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(oi.price) AS monetary
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),

rfm_scores AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency) AS f_score,
        NTILE(5) OVER (ORDER BY monetary) AS m_score
    FROM customer_rfm
)

SELECT
    customer_unique_id,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    CONCAT(r_score, f_score, m_score) AS rfm_score,

    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4
            THEN 'Champions'
        WHEN r_score >= 4 AND f_score >= 3
            THEN 'Loyal Customers'
        WHEN r_score >= 4
            THEN 'Recent Customers'
        WHEN r_score <= 2 AND f_score <= 2
            THEN 'At Risk'
        ELSE 'Others'
    END AS segment

FROM rfm_scores
ORDER BY monetary DESC;