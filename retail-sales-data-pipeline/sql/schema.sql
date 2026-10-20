-- Schéma en étoile (star schema) simple
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_store;

CREATE TABLE dim_product (
    product_id   INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category     TEXT NOT NULL,
    unit_price   REAL NOT NULL CHECK (unit_price > 0)
);

CREATE TABLE dim_store (
    store_id INTEGER PRIMARY KEY,
    city     TEXT NOT NULL
);

CREATE TABLE fact_sales (
    sale_id    INTEGER PRIMARY KEY,
    sale_date  TEXT NOT NULL,
    store_id   INTEGER NOT NULL REFERENCES dim_store(store_id),
    product_id INTEGER NOT NULL REFERENCES dim_product(product_id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    discount   REAL NOT NULL DEFAULT 0 CHECK (discount >= 0 AND discount < 1),
    revenue    REAL NOT NULL
);

CREATE INDEX idx_sales_date  ON fact_sales(sale_date);
CREATE INDEX idx_sales_store ON fact_sales(store_id);
