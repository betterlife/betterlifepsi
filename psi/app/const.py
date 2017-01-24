# PO status definition
PO_STATUS_KEY = u'PURCHASE_ORDER_STATUS'
PO_RECEIVED_STATUS_KEY = u'PURCHASE_ORDER_RECEIVED'
PO_SHIPPED_STATUS_KEY = u'PURCHASE_ORDER_SHIPPED_OUT'
PO_PART_RECEIVED_STATUS_KEY = u'PURCHASE_ORDER_PART_RECEIVED'
PO_DRAFT_STATUS_KEY = u'PURCHASE_ORDER_DRAFT'
PO_ISSUED_STATUS_KEY = u'PURCHASE_ORDER_ISSUED'
PO_REJECTED_STATUS_KEY = u'PURCHASE_ORDER_REJECTED'

# PO type key
PO_TYPE_KEY = u'PURCHASE_ORDER_TYPE'
DIRECT_PO_TYPE_KEY = u'DIRECT_PURCHASE_ORDER'
FRANCHISE_PO_TYPE_KEY = u'FRANCHISE_PURCHASE_ORDER'

# SO type key
SO_TYPE_KEY = u'SALES_ORDER_TYPE'
DIRECT_SO_TYPE_KEY = u'DIRECT_SALES_ORDER'
FRANCHISE_SO_TYPE_KEY = u'FRANCHISE_SALES_ORDER'

# SO Status key
SO_STATUS_KEY = u'SALES_ORDER_STATUS'
SO_CREATED_STATUS_KEY = u'SALES_ORDER_CREATED'
SO_SHIPPED_STATUS_KEY = u'SALES_ORDER_SHIPPED'
SO_DELIVERED_STATUS_KEY = u'SALES_ORDER_DELIVERED'
SO_INVALID_STATUS_KEY = u'SALES_ORDER_INVALID'

# Shipping type key
SHIPPING_TYPE_KEY = u'SHIPPING_TYPE'
DIRECT_SHIPPING_TYPE_KEY = u'DIRECT_SALES_SHIPPING'
FRANCHISE_SHIPPING_TYPE_KEY = u'FRANCHISE_SALES_SHIPPING'


# Inventory transaction type definition key
PURCHASE_IN_INV_TRANS_KEY = u'PURCHASE_IN'
SALES_OUT_INV_TRANS_TYPE_KEY = u'DIRECT_SALES_OUT'
FRANCHISE_SALES_OUT_INV_TRANS_TYPE_KEY = u'FRANCHISE_SALES_OUT'

# Inventory transaction type definition
INVENTORY_TRANSACTION_TYPE_KEY = u'INVENTORY_TRANSACTION_TYPE'
INVENTORY_DAMAGED_TYPE_KEY = u'INVENTORY_DAMAGED'
INVENTORY_LOST_TYPE_KEY = u'INVENTORY_LOST'

# Receiving status definition
RECEIVING_STATUS_KEY = u'RECEIVING_STATUS'
RECEIVING_DRAFT_STATUS_KEY = u'RECEIVING_DRAFT'
RECEIVING_COMPLETE_STATUS_KEY = u'RECEIVING_COMPLETE'

# Shipping status definition
SHIPPING_STATUS_KEY = u'SHIPPING_STATUS'
SHIPPING_COMPLETE_STATUS_KEY = u"SHIPPING_COMPLETE"

# Expense status and type definition key
EXP_TYPE_KEY = u'EXP_TYPE'
EXP_STATUS_KEY = u'EXP_STATUS'

# Incoming status and type definition key
INCOMING_TYPE_KEY = u'INCOMING_TYPE'
INCOMING_STATUS_KEY = u'INCOMING_STATUS'

# Customer related enum value keys
CUSTOMER_JOIN_CHANNEL_KEY = u'CUSTOMER_JOIN_CHANNEL'
CUSTOMER_LEVEL_KEY = u'CUSTOMER_LEVEL'

# User locale settings
LANGUAGE_VALUES_KEY = u'LANGUAGES'
TIMEZONE_VALUES_KEY = u'TIMEZONES'

# Super admin role
SUPER_ADMIN_ROLE_NAME = u'super_admin'

# Organization type key
ORGANIZATION_TYPE_KEY = u'ORGANIZATION_TYPE'
DIRECT_SELLING_STORE_ORG_TYPE_KEY = u'DIRECT_SELLING_STORE'
FRANCHISE_STORE_ORG_TYPE_KEY = u'FRANCHISE_STORE'

# Related type
FRANCHISE_PO_TO_SO_RT_KEY = u'FRANCHISE_PO_TO_SO'

# Report SQLs
SALES_ORDER_AMOUNT_REPORT_SQL = u"""
SELECT
  extract(year from so.order_date) as year,
  extract({0} from so.order_date) as period,
  {1} as period_number,
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

GET_AMOUNT_BY_PERIOD_YEAR = u"""
SELECT
  sum(sol.quantity * sol.unit_price) AS total_amount
FROM sales_Order_line sol, sales_order so
WHERE
  so.id = sol.sales_order_id
    AND extract({0} FROM so.order_date) = {1} AND extract(YEAR FROM so.order_date) = {2}
"""

FILE_HANDLER_LOG_FORMAT = '%(asctime)s %(filename)s.%(funcName)s:%(lineno)d %(name)s:%(levelname)s: %(message)s '

CONSOLE_HANDLER_LOG_FORMAT = '%(asctime)s %(filename)s.%(funcName)s:%(lineno)d %(name)s:%(levelname)s: %(message)s '
