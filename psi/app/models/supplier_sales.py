from datetime import datetime, timedelta
from sqlalchemy.ext.hybrid import hybrid_property

from psi.app.models import Supplier, SalesOrderLine, Product, SalesOrder
from psi.app.utils import format_decimal, date_util
from decimal import Decimal
from sqlalchemy import func, select, Integer

class BaseSupplierSales(Supplier):
    def _get_result(self, select_statement):
        if isinstance(self.id, int):
            result = self.query.session.execute(select_statement).first()
            val = format_decimal(result[0]) if result[0] is not None else Decimal("0.00")
        else:
            val = Decimal("0.00")
        return val

class OverallSupplierSales(BaseSupplierSales):

    @hybrid_property
    def sales_profit(self):
        return self._get_result(OverallSupplierSales._sales_profit_select(self.id))

    @sales_profit.expression
    def sales_profit(self):
        return OverallSupplierSales._sales_profit_select(self.id).label('sales_profit')

    @hybrid_property
    def sales_amount(self):
        return self._get_result(OverallSupplierSales._sales_amount_select(self.id))

    @sales_amount.expression
    def sales_amount(self):
        return OverallSupplierSales._sales_amount_select(self.id).label('sales_amount')

    @hybrid_property
    def daily_profit(self):
        return self._get_result((OverallSupplierSales._daily_profit_select(self.id).group_by(Supplier.create_date)))

    @daily_profit.expression
    def daily_profit(self):
        return OverallSupplierSales._daily_profit_select(self.id).label('daily_profit')

    @hybrid_property
    def daily_amount(self):
        sq = (OverallSupplierSales._daily_amount_select(self.id).group_by(Supplier.create_date))
        return self._get_result(sq)

    @daily_amount.expression
    def daily_amount(self):
        return OverallSupplierSales._daily_amount_select(self.id).label('daily_amount')

    @staticmethod
    def _sales_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.cast(func.date_part('DAY', func.now() - Supplier.create_date), Integer)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(Product.supplier_id == sup_id)
                .where(Product.supplier_id == Supplier.id))

    @staticmethod
    def _daily_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                        / func.cast(func.date_part('DAY', func.now() - Supplier.create_date), Integer)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(Product.supplier_id == sup_id)
                .where(Product.supplier_id == Supplier.id))


class LastMonthSupplierSales(BaseSupplierSales):

    @hybrid_property
    def sales_profit(self):
        return self._get_result(LastMonthSupplierSales._sales_profit_select(self.id))

    @sales_profit.expression
    def sales_profit(self):
        return LastMonthSupplierSales._sales_profit_select(self.id).label('sales_profit')

    @hybrid_property
    def sales_amount(self):
        return self._get_result(LastMonthSupplierSales._sales_amount_select(self.id))

    @sales_amount.expression
    def sales_amount(self):
        return LastMonthSupplierSales._sales_amount_select(self.id).label('sales_amount')

    @hybrid_property
    def daily_profit(self):
        return self._get_result((LastMonthSupplierSales._daily_profit_select(self.id).group_by(Supplier.create_date)))

    @daily_profit.expression
    def daily_profit(self):
        return LastMonthSupplierSales._daily_profit_select(self.id).label('daily_profit')

    @hybrid_property
    def daily_amount(self):
        sq = (LastMonthSupplierSales._daily_amount_select(self.id).group_by(Supplier.create_date))
        return self._get_result(sq)

    @daily_amount.expression
    def daily_amount(self):
        return LastMonthSupplierSales._daily_amount_select(self.id).label('daily_amount')

    @staticmethod
    def _sales_profit_select(sup_id):
        now = datetime.now()
        last_m, last_y = date_util.get_last_month(now.month, now.year)
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('MONTH', SalesOrder.order_date) == last_m)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        now = datetime.now()
        last_m, last_y = date_util.get_last_month(now.month, now.year)
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('MONTH', SalesOrder.order_date) == last_m)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        now = datetime.now()
        last_m, last_y = date_util.get_last_month(now.month, now.year)
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.now() - Supplier.create_date), Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('MONTH', SalesOrder.order_date) == last_m)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_amount_select(sup_id):
        now = datetime.now()
        last_m, last_y = date_util.get_last_month(now.month, now.year)
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.now() - Supplier.create_date),Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('MONTH', SalesOrder.order_date) == last_m )
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(Product.supplier_id == sup_id))


class YesterdaySupplierSales(BaseSupplierSales):

    @hybrid_property
    def sales_profit(self):
        return self._get_result(YesterdaySupplierSales._sales_profit_select(self.id))

    @sales_profit.expression
    def sales_profit(self):
        return YesterdaySupplierSales._sales_profit_select(self.id).label('sales_profit')

    @hybrid_property
    def sales_amount(self):
        return self._get_result(YesterdaySupplierSales._sales_amount_select(self.id))

    @sales_amount.expression
    def sales_amount(self):
        return YesterdaySupplierSales._sales_amount_select(self.id).label('sales_amount')

    @hybrid_property
    def daily_profit(self):
        return self._get_result((YesterdaySupplierSales._daily_profit_select(self.id).group_by(Supplier.create_date)))

    @daily_profit.expression
    def daily_profit(self):
        return YesterdaySupplierSales._daily_profit_select(self.id).label('daily_profit')

    @hybrid_property
    def daily_amount(self):
        sq = (YesterdaySupplierSales._daily_amount_select(self.id).group_by(Supplier.create_date))
        return self._get_result(sq)

    @daily_amount.expression
    def daily_amount(self):
        return YesterdaySupplierSales._daily_amount_select(self.id).label('daily_amount')

    @staticmethod
    def _sales_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date > func.current_date() - 1)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date > func.current_date() - 1)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.now() - Supplier.create_date), Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date > func.current_date() - 1)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.now() - Supplier.create_date),Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date > func.current_date() - 1)
                .where(Product.supplier_id == sup_id))


class LastWeekSupplierSales(BaseSupplierSales):

    @hybrid_property
    def sales_profit(self):
        return self._get_result(LastWeekSupplierSales._sales_profit_select(self.id))

    @sales_profit.expression
    def sales_profit(self):
        return LastWeekSupplierSales._sales_profit_select(self.id).label('sales_profit')

    @hybrid_property
    def sales_amount(self):
        return self._get_result(LastWeekSupplierSales._sales_amount_select(self.id))

    @sales_amount.expression
    def sales_amount(self):
        return LastWeekSupplierSales._sales_amount_select(self.id).label('sales_amount')

    @hybrid_property
    def daily_profit(self):
        return self._get_result((LastWeekSupplierSales._daily_profit_select(self.id).group_by(Supplier.create_date)))

    @daily_profit.expression
    def daily_profit(self):
        return LastWeekSupplierSales._daily_profit_select(self.id).label('daily_profit')

    @hybrid_property
    def daily_amount(self):
        sq = (LastWeekSupplierSales._daily_amount_select(self.id).group_by(Supplier.create_date))
        return self._get_result(sq)

    @daily_amount.expression
    def daily_amount(self):
        return LastWeekSupplierSales._daily_amount_select(self.id).label('daily_amount')

    @staticmethod
    def _sales_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date > func.current_date() - 7)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date > func.current_date() - 7)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.now() - Supplier.create_date), Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date > func.current_date() - 7)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.now() - Supplier.create_date),Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date > func.current_date() - 7)
                .where(Product.supplier_id == sup_id))


class LastQuarterSupplierSales(BaseSupplierSales):

    @hybrid_property
    def sales_profit(self):
        return self._get_result(LastQuarterSupplierSales._sales_profit_select(self.id))

    @sales_profit.expression
    def sales_profit(self):
        return LastQuarterSupplierSales._sales_profit_select(self.id).label('sales_profit')

    @hybrid_property
    def sales_amount(self):
        return self._get_result(LastQuarterSupplierSales._sales_amount_select(self.id))

    @sales_amount.expression
    def sales_amount(self):
        return LastQuarterSupplierSales._sales_amount_select(self.id).label('sales_amount')

    @hybrid_property
    def daily_profit(self):
        return self._get_result((LastQuarterSupplierSales._daily_profit_select(self.id).group_by(Supplier.create_date)))

    @daily_profit.expression
    def daily_profit(self):
        return LastQuarterSupplierSales._daily_profit_select(self.id).label('daily_profit')

    @hybrid_property
    def daily_amount(self):
        sq = (LastQuarterSupplierSales._daily_amount_select(self.id).group_by(Supplier.create_date))
        return self._get_result(sq)

    @daily_amount.expression
    def daily_amount(self):
        return LastQuarterSupplierSales._daily_amount_select(self.id).label('daily_amount')

    @staticmethod
    def _sales_profit_select(sup_id):
        now = datetime.now()
        last_m, last_y = date_util.get_last_month(now.month, now.year)
        # TODO. Get last quarter number
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('MONTH', SalesOrder.order_date) == last_m)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        now = datetime.now()
        last_m, last_y = date_util.get_last_month(now.month, now.year)
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('MONTH', SalesOrder.order_date) == last_m)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        now = datetime.now()
        last_m, last_y = date_util.get_last_month(now.month, now.year)
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.now() - Supplier.create_date), Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('MONTH', SalesOrder.order_date) == last_m)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_amount_select(sup_id):
        now = datetime.now()
        last_m, last_y = date_util.get_last_month(now.month, now.year)
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.now() - Supplier.create_date),Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('MONTH', SalesOrder.order_date) == last_m )
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(Product.supplier_id == sup_id))

