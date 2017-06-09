from datetime import datetime, timedelta
from sqlalchemy.ext.hybrid import hybrid_property

from psi.app.models import Supplier, SalesOrderLine, \
    Product, SalesOrder, EnumValues
from psi.app.utils import format_decimal, date_util
from psi.app.const import SO_DELIVERED_STATUS_KEY 
from decimal import Decimal
from sqlalchemy import func, select, Integer, text


class SupplierSales(Supplier):

    @staticmethod
    def sales_profit_select():
        return select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])

    @staticmethod
    def sales_amount_select():
        return select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)]) 

    @staticmethod
    def daily_profit_select():
        return select([func.cast(func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)
                    / func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date), Integer), 1), Integer)]).as_scalar()

    @staticmethod
    def daily_amount_select():
        return select([func.cast(func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)
                       /func.greatest(func.cast(func.date_part('DAY', func.current_date() - Supplier.create_date),Integer), 1), Integer)]).as_scalar()

    @staticmethod
    def common_where(sel, sup_id):
        return sel.where(SalesOrderLine.product_id == Product.id).where(Product.supplier_id == sup_id)\
                  .where(SalesOrder.id == SalesOrderLine.sales_order_id).where(SalesOrder.status_id == EnumValues.id)\
                  .where(EnumValues.code == SO_DELIVERED_STATUS_KEY).where(Product.supplier_id == Supplier.id)

    def _get_result(self, select_statement):
        if isinstance(self.id, int):
            result = self.query.session.execute(select_statement).first()
            val = format_decimal(result[0]) if (result is not None and result[0] is not None) else Decimal("0.00")
        else:
            val = Decimal("0.00")
        return val

    @staticmethod
    def strip_actual_class(clazz_name):
        """
        The field str(self._sa_class_manager.class_) will return a string like
         <class 'psi.app.models.supplier_sales.ThisYearSupplierSales'>
         So we can get the part ThisYearSupplierSales via substring and
         Then get back the class definition using eval
        :return:
        """
        idx_last_dot = clazz_name.rfind(".") + 1
        right_bound = -2
        clazz = eval(clazz_name[idx_last_dot:right_bound])
        return clazz

    @hybrid_property
    def sales_profit(self):
        clazz = SupplierSales.strip_actual_class(str(self._sa_class_manager.class_))
        return self._get_result(clazz.get_where(SupplierSales.common_where(SupplierSales.sales_profit_select(), self.id)))

    @sales_profit.expression
    def sales_profit(self):
        clazz = SupplierSales.strip_actual_class(str(self._sa_class_manager.class_))
        return clazz.get_where(SupplierSales.common_where(SupplierSales.sales_profit_select(), self.id)).label('sales_profit')

    @hybrid_property
    def sales_amount(self):
        clazz = SupplierSales.strip_actual_class(str(self._sa_class_manager.class_))
        return self._get_result(clazz.get_where(SupplierSales.common_where(SupplierSales.sales_amount_select(), self.id)))

    @sales_amount.expression
    def sales_amount(self):
        clazz = SupplierSales.strip_actual_class(str(self._sa_class_manager.class_))
        return clazz.get_where(SupplierSales.common_where(SupplierSales.sales_amount_select(), self.id)).label('sales_amount')

    @hybrid_property
    def daily_profit(self):
        clazz = SupplierSales.strip_actual_class(str(self._sa_class_manager.class_))
        return self._get_result(clazz.get_where(SupplierSales.common_where(SupplierSales.daily_profit_select(), self.id)).group_by(Supplier.create_date))

    @daily_profit.expression
    def daily_profit(self):
        clazz = SupplierSales.strip_actual_class(str(self._sa_class_manager.class_))
        return clazz.get_where(SupplierSales.common_where(SupplierSales.daily_profit_select(), self.id)).label('daily_profit')

    @hybrid_property
    def daily_amount(self):
        clazz = SupplierSales.strip_actual_class(str(self._sa_class_manager.class_))
        sq = clazz.get_where(SupplierSales.common_where(SupplierSales.daily_amount_select(), self.id)).group_by(Supplier.create_date)
        return self._get_result(sq)

    @daily_amount.expression
    def daily_amount(self):
        clazz = SupplierSales.strip_actual_class(str(self._sa_class_manager.class_))
        return clazz.get_where(SupplierSales.common_where(SupplierSales.daily_amount_select(), self.id))


class OverallSupplierSales(SupplierSales):

    @staticmethod
    def get_where(current_sel):
        return current_sel

    
class LastMonthSupplierSales(SupplierSales):

    @staticmethod
    def get_where(current_sel):
        now = datetime.now()
        last_m, last_y = date_util.get_last_month(now.month, now.year)
        return (current_sel
                .where(func.date_part('MONTH', SalesOrder.order_date) == last_m)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y))


class YesterdaySupplierSales(SupplierSales):

    @staticmethod
    def get_where(current_sel):
        return current_sel.where(SalesOrder.order_date > func.current_date() - text("INTERVAL '1 DAY'"))


class LastWeekSupplierSales(SupplierSales):

    @staticmethod
    def get_where(current_sel):
        return (current_sel
                .where(SalesOrder.order_date > func.date_trunc('week', func.current_date()) - text("INTERVAL '7 DAYS'"))
                .where(SalesOrder.order_date < func.date_trunc('week', func.current_date())))


class LastQuarterSupplierSales(SupplierSales):

    @staticmethod
    def get_where(current_sel):
        now = datetime.now()
        last_q, last_y = date_util.get_last_quarter(now.month, now.year)
        return (current_sel
                .where(func.date_part('QUARTER', SalesOrder.order_date) == last_q)
                .where(func.date_part('YEAR', SalesOrder.order_date) == last_y))


class ThisQuarterSupplierSales(SupplierSales):

    @staticmethod
    def get_where(current_sel):
        now = datetime.now()
        this_q, this_y = (now.month - 1) // 3 + 1, now.year
        return (current_sel.where(func.date_part('QUARTER', SalesOrder.order_date) == this_q)
                .where(func.date_part('YEAR', SalesOrder.order_date) == this_y))

class LastYearSupplierSales(SupplierSales):

    @staticmethod
    def get_where(current_sel):
        last_y = datetime.now().year - 1
        return current_sel.where(func.date_part('YEAR', SalesOrder.order_date) == last_y)


class TodaySupplierSales(SupplierSales):

    @staticmethod
    def get_where(current_sel):
        return current_sel.where(SalesOrder.order_date >= func.current_date())


class ThisWeekSupplierSales(SupplierSales):

    @staticmethod
    def get_where(current_sel):
        return current_sel.where(SalesOrder.order_date >= func.date_trunc('week', func.current_date()))


class ThisMonthSupplierSales(SupplierSales):

    @staticmethod
    def get_where(current_sel):
        return current_sel.where(SalesOrder.order_date >= func.date_trunc('month', func.current_date()))


class ThisYearSupplierSales(SupplierSales):

    @staticmethod
    def get_where(current_sel):
        return current_sel.where(func.date_part('YEAR', SalesOrder.order_date) == datetime.now().year)
