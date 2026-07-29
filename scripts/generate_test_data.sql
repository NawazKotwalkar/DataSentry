-- ============================================================
-- DataSentry test data generator
-- Creates two tables, each with 50,000 rows, with intentional
-- data quality issues planted in for testing the audit engine.
--
-- Run with: psql "your_connection_string" -f generate_test_data.sql
-- ============================================================

-- ------------------------------------------------------------
-- Table 1: customers (50,000 rows)
-- Planted issues: nulls in email, duplicate customer_ids,
-- inconsistent status values, a few outlier signup_bonus values
-- ------------------------------------------------------------

DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id   INTEGER,
    full_name     TEXT,
    email         TEXT,
    signup_date   DATE,
    status        TEXT,
    signup_bonus  NUMERIC
);

INSERT INTO customers (customer_id, full_name, email, signup_date, status, signup_bonus)
SELECT
    -- ~2% duplicate IDs on purpose
    CASE WHEN random() < 0.02 THEN (n % 1000) ELSE n END AS customer_id,
    'Customer ' || n AS full_name,
    -- ~5% null emails, ~3% malformed emails
    CASE
        WHEN random() < 0.05 THEN NULL
        WHEN random() < 0.03 THEN 'not-an-email-' || n
        ELSE 'customer' || n || '@example.com'
    END AS email,
    (DATE '2023-01-01' + (random() * 900)::int) AS signup_date,
    -- inconsistent status casing/values on purpose
    (ARRAY['active', 'inactive', 'pending', 'Active', 'ACTIVE', 'unknown'])[floor(random() * 6 + 1)] AS status,
    -- ~1% extreme outlier bonuses
    CASE
        WHEN random() < 0.01 THEN (random() * 100000)::numeric(10,2)
        ELSE (random() * 200)::numeric(10,2)
    END AS signup_bonus
FROM generate_series(1, 50000) AS n;

-- ------------------------------------------------------------
-- Table 2: orders (50,000 rows)
-- Planted issues: negative order amounts, nulls in shipped_date,
-- duplicate order_ids, a handful of extreme outlier amounts
-- ------------------------------------------------------------

DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    order_id       INTEGER,
    customer_id    INTEGER,
    order_amount   NUMERIC,
    order_date     DATE,
    shipped_date   DATE,
    payment_method TEXT
);

INSERT INTO orders (order_id, customer_id, order_amount, order_date, shipped_date, payment_method)
SELECT
    CASE WHEN random() < 0.015 THEN (n % 2000) ELSE n END AS order_id,
    (floor(random() * 50000) + 1)::int AS customer_id,
    -- ~2% negative amounts (data entry errors), ~0.5% extreme outliers
    CASE
        WHEN random() < 0.02 THEN -1 * (random() * 500)::numeric(10,2)
        WHEN random() < 0.005 THEN (random() * 50000)::numeric(10,2)
        ELSE (random() * 300)::numeric(10,2)
    END AS order_amount,
    (DATE '2024-01-01' + (random() * 550)::int) AS order_date,
    -- ~10% never shipped (null)
    CASE
        WHEN random() < 0.10 THEN NULL
        ELSE (DATE '2024-01-01' + (random() * 560)::int)
    END AS shipped_date,
    (ARRAY['credit_card', 'paypal', 'bank_transfer', 'cod', 'Credit_Card'])[floor(random() * 5 + 1)] AS payment_method
FROM generate_series(1, 50000) AS n;

-- ------------------------------------------------------------
-- Sanity checks — row counts and a peek at planted issues
-- ------------------------------------------------------------

SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'orders', COUNT(*) FROM orders;

SELECT COUNT(*) AS null_emails FROM customers WHERE email IS NULL;
SELECT COUNT(*) AS negative_orders FROM orders WHERE order_amount < 0;
SELECT COUNT(*) AS unshipped_orders FROM orders WHERE shipped_date IS NULL;
