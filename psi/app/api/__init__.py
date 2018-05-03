# encoding=utf-8
from .sales_order import SalesOrderApi


def init_all_apis(api):
    api.add_resource(SalesOrderApi, '/api/sales_order/<int:sales_order_id>')
