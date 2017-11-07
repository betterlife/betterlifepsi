SALES_AMOUNT_REPORT_SQL = u"""
SELECT
  extract(year from so.order_date) as year,
  extract({0} from so.order_date) as period,
  to_char(so.order_date,'{1}') as period_number,
  sum(sol.quantity * sol.unit_price) as total_amount
FROM sales_order_line sol, sales_order so
WHERE so.id = sol.sales_order_id
group by year, period, period_number
order by year desc, period desc limit {2};
"""

SALES_ORDER_WEEKLY_AMOUNT_REPORT_SQL = u"""
SELECT
  extract(YEAR FROM so.order_date)   AS year,
  extract(WEEK FROM so.order_date)   AS period,
  sum(sol.quantity * sol.unit_price) AS total_amount
FROM sales_order_line sol, sales_order so
WHERE so.id = sol.sales_order_id
GROUP BY year, period
ORDER BY year DESC, period DESC
LIMIT {0}"""


PERIOD_ON_PERIOD_AMOUNT_REPORT_SQL = u"""
SELECT
  extract(YEAR FROM so.order_date)   AS yyyy,
  extract({0} FROM so.order_date) AS period,
  sum(sol.quantity * sol.unit_price) AS total_amount
FROM sales_Order_line sol, sales_order so
WHERE
  so.id = sol.sales_order_id
  AND (extract({0} FROM so.order_date) = extract({0} FROM CURRENT_TIMESTAMP)
  AND extract(YEAR FROM so.order_date) in (extract(YEAR FROM so.order_date), extract(YEAR FROM so.order_date)-1 ))
GROUP BY yyyy, period ORDER BY yyyy DESC;
"""

PERIOD_ON_PERIOD_PROFIT_REPORT_SQL = u"""
SELECT
  extract(YEAR FROM link.out_date) AS yyyy,
  extract({0} FROM link.out_date) AS period,
  sum(link.out_quantity * (link.out_price - link.in_price)) AS profit
FROM inventory_in_out_link link
WHERE
  (extract({0} FROM link.out_date) = extract({0} FROM CURRENT_TIMESTAMP)
  AND extract(YEAR FROM link.out_date) in (extract(YEAR FROM link.out_date), extract(YEAR FROM link.out_date)-1 ))
GROUP BY yyyy, period ORDER BY yyyy DESC;
"""

GET_AMOUNT_BY_YEAR_SQL = u"""
SELECT
  sum(sol.quantity * sol.unit_price) AS total_amount
FROM sales_Order_line sol, sales_order so
WHERE so.id = sol.sales_order_id AND extract({0} FROM so.order_date) = {1} AND extract(YEAR FROM so.order_date) = {2}
"""

GET_PROFIT_BY_YEAR_SQL = u"""
SELECT
  sum(link.out_quantity * (link.out_price - link.in_price)) AS total_profit
FROM inventory_in_out_link link
WHERE extract({0} FROM link.out_date) = {1} AND extract(YEAR FROM link.out_date) = {2}
"""

SALES_PROFIT_REPORT_SQL = u"""
SELECT
    extract(YEAR FROM link.out_date)   AS yyyy,
    extract({0} FROM link.out_date) AS period,
    sum(link.out_quantity * link.out_price) AS out_amount,
    sum(link.out_quantity * (link.out_price-link.in_price)) as profit
FROM inventory_in_out_link link 
WHERE
  extract(YEAR FROM link.out_date) in (extract(YEAR FROM link.out_date), extract(YEAR FROM link.out_date)-1 )
GROUP BY yyyy, period 
ORDER BY yyyy ASC, period ASC 
LIMIT {1};
"""

ALL_SALES_PROFIT_SQL = u"""
SELECT 
    sum((sales_order_line.unit_price - product.purchase_price) * sales_order_line.quantity) as total
FROM 
    sales_order_line, product, supplier, sales_order, enum_values
WHERE 
    sales_order_line.product_id = product.id 
    AND product.supplier_id = supplier.id 
    AND sales_order.id = sales_order_line.sales_order_id 
    AND sales_order.status_id = enum_values.id 
    AND enum_values.code = 'SALES_ORDER_DELIVERED'
"""
