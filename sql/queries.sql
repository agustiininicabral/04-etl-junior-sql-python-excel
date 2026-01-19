-- Ventas netas por día
SELECT order_date, SUM(net_amount) AS net_sales
FROM stg_order
GROUP BY 1
ORDER BY 1;

-- Top productos por ventas netas
SELECT product_id, SUM(net_amount) AS net_sales
FROM stg_order
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10;