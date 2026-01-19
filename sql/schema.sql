CREATE TABLE IF NOT EXISTS stg_order (
  order_id      INT PRIMARY KEY,
  order_date    DATE NOT NULL,
  customer_id   INT NOT NULL,
  product_id    INT NOT NULL,
  quantity      INT NOT NULL,
  unit_price    NUMERIC(10,2) NOT NULL,
  discount_rate NUMERIC(5,2) NOT NULL,
  net_amount    NUMERIC(12,2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_stg_order_date ON stg_order(order_date);