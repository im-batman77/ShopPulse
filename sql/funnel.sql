

-- Funnel Analysis


SELECT
    event_type AS step_name,
    COUNT(DISTINCT customer_id) AS user_count
FROM website_events
GROUP BY event_type
ORDER BY
    CASE event_type
        WHEN 'page_view' THEN 1
        WHEN 'add_to_cart' THEN 2
        WHEN 'checkout' THEN 3
        WHEN 'purchase' THEN 4
    END;