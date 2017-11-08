from decimal import Decimal

from sqlalchemy.exc import ProgrammingError

from psi.app.models import SalesOrderLine, Product
from psi.app.utils import format_decimal
from sqlalchemy import func, select


class ReportBaseModel(object):
    def _get_result(self, select_statement):
        if isinstance(self.id, int):
            result = self.query.session.execute(select_statement).first()
            val = format_decimal(result[0]) if (result is not None and result[0] is not None) else Decimal("0.00")
        else:
            val = Decimal("0.00")
        return val

    @staticmethod
    def get_all_profit():
        from psi.app.reports.sqls import ALL_SALES_PROFIT_SQL
        from psi.app.utils import db_util
        try:
            total = db_util.get_result_raw_sql(ALL_SALES_PROFIT_SQL)
            return total[0]
        except ProgrammingError:
            return 0

    @staticmethod
    def sales_profit_select():
        return select([func.sum((SalesOrderLine.unit_price - Product.purchase_price) * SalesOrderLine.quantity)])

    @staticmethod
    def sales_amount_select():
        return select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)])

    @staticmethod
    def strip_actual_class(clazz_name):
        from psi.app.models.supplier_sales import OverallSupplierSales, \
            LastMonthSupplierSales, YesterdaySupplierSales, \
            LastWeekSupplierSales, LastQuarterSupplierSales, \
            ThisQuarterSupplierSales, LastYearSupplierSales, TodaySupplierSales, \
            ThisWeekSupplierSales, ThisMonthSupplierSales, ThisYearSupplierSales

        from psi.app.models.product_sales import OverallProductSales, \
            LastMonthProductSales, LastQuarterProductSales, LastWeekProductSales, \
            LastYearProductSales, ThisMonthProductSales, ThisQuarterProductSales, \
            ThisWeekProductSales, ThisYearProductSales, TodayProductSales, \
            YesterdayProductSales

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
