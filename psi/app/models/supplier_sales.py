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
            val = format_decimal(result[0]) if (result is not None and result[0] is not None) else Decimal("0.00")
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
                        / func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(Product.supplier_id == sup_id)
                .where(Product.supplier_id == Supplier.id))

    @staticmethod
    def _daily_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                        / func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer)])
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
                        / func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer), 1)])
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
                        / func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date),Integer), 1)])
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
                .where(SalesOrder.order_date < func.current_date())
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date > func.current_date() - 1)
                .where(SalesOrder.order_date < func.current_date())
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date > func.current_date() - 1)
                .where(SalesOrder.order_date < func.current_date())
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date),Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date > func.current_date() - 1)
                .where(SalesOrder.order_date < func.current_date())
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
                        / func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date > func.current_date() - 7)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date),Integer), 1)])
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
        last_q, last_y = date_util.get_last_quarter(now.month, now.year)
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('QUARTER', SalesOrder.order_date) == last_q)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        now = datetime.now()
        last_q, last_y = date_util.get_last_quarter(now.month, now.year)
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('QUARTER', SalesOrder.order_date) == last_q)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        now = datetime.now()
        last_q, last_y = date_util.get_last_quarter(now.month, now.year)
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('QUARTER', SalesOrder.order_date) == last_q)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_amount_select(sup_id):
        now = datetime.now()
        last_q, last_y = date_util.get_last_quarter(now.month, now.year)
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                 / func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer)])
         .where(SalesOrderLine.product_id == Product.id)
         .where(Product.supplier_id == sup_id)
         .where(SalesOrder.id == SalesOrderLine.sales_order_id)
         .where(func.date_part('QUARTER', SalesOrder.order_date) == last_q)
         .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
         .where(Product.supplier_id == Supplier.id))

class ThisQuarterSupplierSales(BaseSupplierSales):

    @hybrid_property
    def sales_profit(self):
        return self._get_result(ThisQuarterSupplierSales._sales_profit_select(self.id))

    @sales_profit.expression
    def sales_profit(self):
        return ThisQuarterSupplierSales._sales_profit_select(self.id).label('sales_profit')

    @hybrid_property
    def sales_amount(self):
        return self._get_result(ThisQuarterSupplierSales._sales_amount_select(self.id))

    @sales_amount.expression
    def sales_amount(self):
        return LastQuarterSupplierSales._sales_amount_select(self.id).label('sales_amount')

    @hybrid_property
    def daily_profit(self):
        return self._get_result((ThisQuarterSupplierSales._daily_profit_select(self.id).group_by(Supplier.create_date)))

    @daily_profit.expression
    def daily_profit(self):
        return ThisQuarterSupplierSales._daily_profit_select(self.id).label('daily_profit')

    @hybrid_property
    def daily_amount(self):
        sq = (ThisQuarterSupplierSales._daily_amount_select(self.id).group_by(Supplier.create_date))
        return self._get_result(sq)

    @daily_amount.expression
    def daily_amount(self):
        return ThisQuarterSupplierSales._daily_amount_select(self.id).label('daily_amount')

    @staticmethod
    def _sales_profit_select(sup_id):
        now = datetime.now()
        this_q, this_y = (now.month - 1) // 3 + 1, now.year
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('QUARTER', SalesOrder.order_date) == this_q)
                .where(func.date_part('YEAR', SalesOrder.order_date) == this_y)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        now = datetime.now()
        this_q, this_y = (now.month - 1) // 3 + 1, now.year
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('QUARTER', SalesOrder.order_date) == this_q)
                .where(func.date_part('YEAR', SalesOrder.order_date) == this_y)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        now = datetime.now()
        this_q, this_y = (now.month - 1) // 3 + 1, now.year
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('QUARTER', SalesOrder.order_date) == this_q)
                .where(func.date_part('YEAR', SalesOrder.order_date) == this_y)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_amount_select(sup_id):
        now = datetime.now()
        this_q, this_y = (now.month - 1) // 3 + 1, now.year
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                 / func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer)])
         .where(SalesOrderLine.product_id == Product.id)
         .where(Product.supplier_id == sup_id)
         .where(SalesOrder.id == SalesOrderLine.sales_order_id)
         .where(func.date_part('QUARTER', SalesOrder.order_date) == this_q)
         .where(func.date_part('YEAR', SalesOrder.order_date) == this_y)
         .where(Product.supplier_id == Supplier.id))


class LastYearSupplierSales(BaseSupplierSales):

    @hybrid_property
    def sales_profit(self):
        return self._get_result(LastYearSupplierSales._sales_profit_select(self.id))

    @sales_profit.expression
    def sales_profit(self):
        return LastYearSupplierSales._sales_profit_select(self.id).label('sales_profit')

    @hybrid_property
    def sales_amount(self):
        return self._get_result(LastYearSupplierSales._sales_amount_select(self.id))

    @sales_amount.expression
    def sales_amount(self):
        return LastYearSupplierSales._sales_amount_select(self.id).label('sales_amount')

    @hybrid_property
    def daily_profit(self):
        return self._get_result((LastYearSupplierSales._daily_profit_select(self.id).group_by(Supplier.create_date)))

    @daily_profit.expression
    def daily_profit(self):
        return LastYearSupplierSales._daily_profit_select(self.id).label('daily_profit')

    @hybrid_property
    def daily_amount(self):
        sq = (LastYearSupplierSales._daily_amount_select(self.id).group_by(Supplier.create_date))
        return self._get_result(sq)

    @daily_amount.expression
    def daily_amount(self):
        return LastYearSupplierSales._daily_amount_select(self.id).label('daily_amount')

    @staticmethod
    def _sales_profit_select(sup_id):
        last_y = datetime.now().year - 1
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        last_y = datetime.now().year - 1
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        last_y = datetime.now().year - 1
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(Product.supplier_id == sup_id)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(Product.supplier_id == Supplier.id))

    @staticmethod
    def _daily_amount_select(sup_id):
        last_y = datetime.now().year - 1
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                 / func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer)])
         .where(SalesOrderLine.product_id == Product.id)
         .where(Product.supplier_id == sup_id)
         .where(SalesOrder.id == SalesOrderLine.sales_order_id)
         .where(func.date_part('YEAR', SalesOrder.order_date) == last_y)
         .where(Product.supplier_id == Supplier.id))

class TodaySupplierSales(BaseSupplierSales):

    @hybrid_property
    def sales_profit(self):
        return self._get_result(TodaySupplierSales._sales_profit_select(self.id))

    @sales_profit.expression
    def sales_profit(self):
        return TodaySupplierSales._sales_profit_select(self.id).label('sales_profit')

    @hybrid_property
    def sales_amount(self):
        return self._get_result(TodaySupplierSales._sales_amount_select(self.id))

    @sales_amount.expression
    def sales_amount(self):
        return TodaySupplierSales._sales_amount_select(self.id).label('sales_amount')

    @hybrid_property
    def daily_profit(self):
        return self._get_result((TodaySupplierSales._daily_profit_select(self.id).group_by(Supplier.create_date)))

    @daily_profit.expression
    def daily_profit(self):
        return TodaySupplierSales._daily_profit_select(self.id).label('daily_profit')

    @hybrid_property
    def daily_amount(self):
        sq = (TodaySupplierSales._daily_amount_select(self.id).group_by(Supplier.create_date))
        return self._get_result(sq)

    @daily_amount.expression
    def daily_amount(self):
        return TodaySupplierSales._daily_amount_select(self.id).label('daily_amount')

    @staticmethod
    def _sales_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date >= func.current_date())
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date >= func.current_date())
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date >= func.current_date())
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date),Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date >= func.current_date())
                .where(Product.supplier_id == sup_id))

class ThisWeekSupplierSales(BaseSupplierSales):

    @hybrid_property
    def sales_profit(self):
        return self._get_result(ThisWeekSupplierSales._sales_profit_select(self.id))

    @sales_profit.expression
    def sales_profit(self):
        return ThisWeekSupplierSales._sales_profit_select(self.id).label('sales_profit')

    @hybrid_property
    def sales_amount(self):
        return self._get_result(ThisWeekSupplierSales._sales_amount_select(self.id))

    @sales_amount.expression
    def sales_amount(self):
        return ThisWeekSupplierSales._sales_amount_select(self.id).label('sales_amount')

    @hybrid_property
    def daily_profit(self):
        return self._get_result((ThisWeekSupplierSales._daily_profit_select(self.id).group_by(Supplier.create_date)))

    @daily_profit.expression
    def daily_profit(self):
        return ThisWeekSupplierSales._daily_profit_select(self.id).label('daily_profit')

    @hybrid_property
    def daily_amount(self):
        sq = (ThisWeekSupplierSales._daily_amount_select(self.id).group_by(Supplier.create_date))
        return self._get_result(sq)

    @daily_amount.expression
    def daily_amount(self):
        return ThisWeekSupplierSales._daily_amount_select(self.id).label('daily_amount')

    @staticmethod
    def _sales_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.order_date >= func.current_date())
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.order_date >= func.current_date())
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(Product.supplier_id == sup_id)
                .where(SalesOrder.order_date >= func.current_date())
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(Product.supplier_id == Supplier.id))

    @staticmethod
    def _daily_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                 / func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer)])
         .where(SalesOrderLine.product_id == Product.id)
         .where(Product.supplier_id == sup_id)
         .where(SalesOrder.order_date >= func.current_date())
         .where(Product.supplier_id == Supplier.id))

class ThisMonthSupplierSales(BaseSupplierSales):

    @hybrid_property
    def sales_profit(self):
        return self._get_result(ThisMonthSupplierSales._sales_profit_select(self.id))

    @sales_profit.expression
    def sales_profit(self):
        return ThisMonthSupplierSales._sales_profit_select(self.id).label('sales_profit')

    @hybrid_property
    def sales_amount(self):
        return self._get_result(ThisMonthSupplierSales._sales_amount_select(self.id))

    @sales_amount.expression
    def sales_amount(self):
        return ThisMonthSupplierSales._sales_amount_select(self.id).label('sales_amount')

    @hybrid_property
    def daily_profit(self):
        return self._get_result((ThisMonthSupplierSales._daily_profit_select(self.id).group_by(Supplier.create_date)))

    @daily_profit.expression
    def daily_profit(self):
        return ThisMonthSupplierSales._daily_profit_select(self.id).label('daily_profit')

    @hybrid_property
    def daily_amount(self):
        sq = (ThisMonthSupplierSales._daily_amount_select(self.id).group_by(Supplier.create_date))
        return self._get_result(sq)

    @daily_amount.expression
    def daily_amount(self):
        return ThisMonthSupplierSales._daily_amount_select(self.id).label('daily_amount')

    @staticmethod
    def _sales_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.order_date >= func.date_trunc('month', func.current_date()))
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(SalesOrder.order_date >= func.date_trunc('month', func.current_date()))
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(Product.supplier_id == sup_id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(SalesOrder.order_date >= func.date_trunc('month', func.current_date()))
                .where(Product.supplier_id == Supplier.id))

    @staticmethod
    def _daily_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                 / func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer)])
         .where(SalesOrderLine.product_id == Product.id)
         .where(Product.supplier_id == sup_id)
         .where(SalesOrder.id == SalesOrderLine.sales_order_id)
         .where(SalesOrder.order_date >= func.date_trunc('month', func.current_date()))
         .where(Product.supplier_id == Supplier.id))

class ThisYearSupplierSales(BaseSupplierSales):

    @hybrid_property
    def sales_profit(self):
        return self._get_result(ThisYearSupplierSales._sales_profit_select(self.id))

    @sales_profit.expression
    def sales_profit(self):
        return ThisYearSupplierSales._sales_profit_select(self.id).label('sales_profit')

    @hybrid_property
    def sales_amount(self):
        return self._get_result(ThisYearSupplierSales._sales_amount_select(self.id))

    @sales_amount.expression
    def sales_amount(self):
        return ThisYearSupplierSales._sales_amount_select(self.id).label('sales_amount')

    @hybrid_property
    def daily_profit(self):
        return self._get_result((ThisYearSupplierSales._daily_profit_select(self.id).group_by(Supplier.create_date)))

    @daily_profit.expression
    def daily_profit(self):
        return ThisYearSupplierSales._daily_profit_select(self.id).label('daily_profit')

    @hybrid_property
    def daily_amount(self):
        sq = (ThisYearSupplierSales._daily_amount_select(self.id).group_by(Supplier.create_date))
        return self._get_result(sq)

    @daily_amount.expression
    def daily_amount(self):
        return ThisYearSupplierSales._daily_amount_select(self.id).label('daily_amount')

    @staticmethod
    def _sales_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(func.date_part('YEAR', SalesOrder.order_date) == datetime.now().year)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _sales_amount_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(func.date_part('YEAR', SalesOrder.order_date) == datetime.now().year)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(Product.supplier_id == sup_id))

    @staticmethod
    def _daily_profit_select(sup_id):
        return (select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                        / func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer), 1)])
                .where(SalesOrderLine.product_id == Product.id)
                .where(Product.supplier_id == sup_id)
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(func.date_part('YEAR', SalesOrder.order_date) == datetime.now().year))

    @staticmethod
    def _daily_amount_select(sup_id):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)/func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date),Integer), 1)])
         .where(SalesOrderLine.product_id == Product.id)
         .where(Product.supplier_id == sup_id)
         .where(SalesOrder.id == SalesOrderLine.sales_order_id)
         .where(func.date_part('YEAR', SalesOrder.order_date) == datetime.now().year))
