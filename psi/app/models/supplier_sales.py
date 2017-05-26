from datetime import datetime 
from sqlalchemy.ext.hybrid import hybrid_property

from psi.app.models import Supplier, SalesOrderLine, Product
from psi.app.reports.sqls import SUPPLIER_AMOUNT_SQL, SUPPLIER_PROFIT_SQL, SALES_DATE_SQL
from psi.app.service import Info
from psi.app.utils import format_decimal
from decimal import Decimal
from sqlalchemy import func, select

db = Info.get_db()


# TODO: This report should be constructed based on sales order line model, not supplier mode. 
class SupplierSales(Supplier):

    @hybrid_property
    def sales_profit(self):
        if isinstance(self.id, int):
            result = db.engine.execute(SUPPLIER_PROFIT_SQL.format(supplier_id=str(self.id))).fetchall()
            sales_profit = format_decimal(float(result[0][0])) if (len(result) > 0 and result[0][0] is not None) else Decimal(0.00)
        else:
            sales_profit = Decimal("0.00")
        return sales_profit

    @sales_profit.expression
    def sales_profit(self):
        return(select([func.sum((SalesOrderLine.unit_price - Product.purchase_price)*SalesOrderLine.quantity)])
               .where(SalesOrderLine.product_id == Product.id)
               .where(Product.supplier_id == self.id)
               .label('sales_profit'))

    @hybrid_property
    def sales_amount(self):
        if isinstance(self.id, int):
            result = db.engine.execute(SUPPLIER_AMOUNT_SQL.format(supplier_id=str(self.id))).fetchall()
            sales_amount = format_decimal(float(result[0][0])) if (len(result) > 0 and result[0][0] is not None) else Decimal(0.00)
        else:
            sales_amount = Decimal(0.00)
        return format_decimal(sales_amount)

    @sales_amount.expression
    def sales_amount(self):
        return(select([func.sum(SalesOrderLine.unit_price*SalesOrderLine.quantity)])
               .where(SalesOrderLine.product_id == Product.id)
               .where(Product.supplier_id == self.id)
               .label('sales_amount'))

    @hybrid_property
    def daily_profit(self):
        if isinstance(self.id, int):
            days = (datetime.now() - self.create_date).days
            days = 1 if days == 0 else days
            profit = self.sales_profit/days if days != 0 else self.sales_profit
        else:
            profit = Decimal(0.00)
        return format_decimal(profit)

    @daily_profit.expression
    def daily_profit(self):
        return(select([func.sum((SalesOrderLine.unit_price - Product.purchase_price)*SalesOrderLine.quantity)/func.date_part('DAY', func.now()-Supplier.create_date)])
               .where(SalesOrderLine.product_id == Product.id)
               .where(Product.supplier_id == self.id)
               .where(Product.supplier_id == Supplier.id)
               .label('daily_profit'))

    @hybrid_property
    def daily_amount(self):
        if isinstance(self.id, int):
            days = (datetime.now() - self.create_date).days
            days = 1 if days == 0 else days
            amount = self.sales_amount/days if days != 0 else self.sales_amount
        else:
            amount = Decimal(0.00)
        return format_decimal(amount)

    @daily_amount.expression
    def daily_amount(self):
        return(select([func.sum(SalesOrderLine.unit_price*SalesOrderLine.quantity)/func.date_part('DAY', func.now()-Supplier.create_date)])
               .where(SalesOrderLine.product_id == Product.id)
               .where(Product.supplier_id == self.id)
               .where(Product.supplier_id == Supplier.id)
               .label('daily_amount'))
