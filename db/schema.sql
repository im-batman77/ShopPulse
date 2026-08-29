-- ShopPulse E-Commerce Analytics Star Schema

-- 1. Dimensions

CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix INT,
    customer_city VARCHAR(100),
    customer_state VARCHAR(5)
);

CREATE TABLE ab_test_assignments (
    customer_id VARCHAR(50) PRIMARY KEY,
    test_group VARCHAR(20) -- 'control' or 'treatment'
);

-- 2. Facts

CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_status VARCHAR(20),
    order_purchase_timestamp DATETIME2,
    order_approved_at DATETIME2,
    order_delivered_carrier_date DATETIME2,
    order_delivered_customer_date DATETIME2,
    order_estimated_delivery_date DATETIME2
);

CREATE TABLE order_items (
    order_id VARCHAR(50),
    order_item_id INT,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date DATETIME2,
    price DECIMAL(12,2),
    freight_value DECIMAL(12,2)
);

CREATE TABLE website_events (
    event_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id VARCHAR(50),
    event_type VARCHAR(50), -- 'page_view', 'add_to_cart', 'checkout', 'purchase'
    event_time DATETIME2
);

-- Indexes for performance

CREATE INDEX idx_orders_customer
ON orders(customer_id);

CREATE INDEX idx_events_customer
ON website_events(customer_id);

CREATE INDEX idx_order_items_order
ON order_items(order_id);