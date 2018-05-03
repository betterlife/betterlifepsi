from sqlalchemy import select, func, or_
from sqlalchemy.ext.hybrid import hybrid_property

from psi.app import const
from psi.app.models import Product, InventoryTransactionLine, \
    InventoryTransaction
from psi.app.service import Info
from psi.app.utils import format_decimal, get_weeks_between

db = Info.get_db()

class ProductInventory(Product):

    @hybrid_property
    def inventory_advice(self):
        from psi.app.advice import InventoryAdvice
        return InventoryAdvice.advice(self)

    @inventory_advice.setter
    def inventory_advice(self, value):
        pass

    @inventory_advice.expression
    def inventory_advice(self):
        pass

    @hybrid_property
    def average_purchase_price(self):
        return self.cal_inv_trans_average(const.PURCHASE_IN_INV_TRANS_KEY)

    @average_purchase_price.setter
    def average_purchase_price(self, val):
        pass

    @average_purchase_price.expression
    def average_purchase_price(self):
        from psi.app.models import EnumValues
        return (select([func.sum(InventoryTransactionLine.quantity * InventoryTransactionLine.price) /
                        func.sum(InventoryTransactionLine.quantity)])
                .where(self.id == InventoryTransactionLine.product_id
                       and InventoryTransactionLine.inventory_transaction_id == InventoryTransaction.id
                       and InventoryTransaction.type_id == EnumValues.id
                       and EnumValues.code == const.PURCHASE_IN_INV_TRANS_KEY)
                .label('average_purchase_price'))

    @hybrid_property
    def average_retail_price(self):
        return self.cal_inv_trans_average(const.SALES_OUT_INV_TRANS_TYPE_KEY)

    @average_retail_price.setter
    def average_retail_price(self, val):
        pass

    @average_retail_price.expression
    def average_retail_price(self):
        from psi.app.models import EnumValues
        return (select([func.sum(InventoryTransactionLine.quantity * InventoryTransactionLine.price) /
                        func.greatest(func.sum(InventoryTransactionLine.quantity), 1)])
                .where(self.id == InventoryTransactionLine.product_id
                       and InventoryTransactionLine.inventory_transaction_id == InventoryTransaction.id
                       and InventoryTransaction.type_id == EnumValues.id
                       and EnumValues.code == const.SALES_OUT_INV_TRANS_TYPE_KEY)
                .label('average_retail_price'))

    @hybrid_property
    def average_unit_profit(self):
        if self.average_purchase_price != 0 and self.average_retail_price != 0:
            return self.average_retail_price - self.average_purchase_price
        return 0

    @average_unit_profit.setter
    def average_unit_profit(self, value):
        pass

    @average_unit_profit.expression
    def average_unit_profit(self):
        from .enum_values import EnumValues
        return ((select([-func.sum(InventoryTransactionLine.quantity * InventoryTransactionLine.price) /
                         func.greatest(func.sum(InventoryTransactionLine.quantity), 1)])
                 .where(self.id == InventoryTransactionLine.product_id)
                 .where(InventoryTransactionLine.inventory_transaction_id == InventoryTransaction.id)
                 .where(InventoryTransaction.type_id == EnumValues.id)
                 .where(or_(EnumValues.code == const.SALES_OUT_INV_TRANS_TYPE_KEY, EnumValues.code == const.PURCHASE_IN_INV_TRANS_KEY)))
                .label('average_unit_profit'))

    @hybrid_property
    def weekly_average_profit(self):
        if 0 == self.average_unit_profit:
            return 0
        return format_decimal(self.weekly_sold_qty * self.average_unit_profit)

    @weekly_average_profit.expression
    def weekly_average_profit(self):
        from .enum_values import EnumValues
        return ((select([-func.sum(InventoryTransactionLine.quantity * InventoryTransactionLine.price) /
                         func.greatest(func.sum(InventoryTransactionLine.quantity), 1)])
                 .where(self.id == InventoryTransactionLine.product_id
                        and InventoryTransactionLine.inventory_transaction_id == InventoryTransaction.id
                        and InventoryTransaction.type_id == EnumValues.id
                        and (EnumValues.code == const.SALES_OUT_INV_TRANS_TYPE_KEY or
                             EnumValues.code == const.PURCHASE_IN_INV_TRANS_KEY)))
                .label('weekly_average_profit'))

    @weekly_average_profit.setter
    def weekly_average_profit(self, value):
        pass

    @hybrid_property
    def gross_profit_rate(self):
        if self.average_retail_price != 0 and self.average_purchase_price != 0:
            val = (self.average_retail_price - self.average_purchase_price)/self.average_purchase_price
            try:
                fval = float(val)
                percent = "{:.2%}".format(fval)
                return percent
            except Exception as e:
                return '-'
        return '-'

    @gross_profit_rate.setter
    def gross_profit_rate(self, value):
        pass

    @hybrid_property
    def weekly_sold_qty(self):
        """
        SQL:
        SELECT p.id, p.name,
          -sum(itl.quantity),
          -sum(itl.quantity) / (greatest(date_part('days', max(it.date) - min(it.date)), 1)/7),
        FROM
          inventory_transaction_line itl,
          inventory_transaction it,
          enum_values ev,
          product p
        where
          itl.inventory_transaction_id = it.id
          AND itl.product_id = p.id
          AND ev.code = 'SALES_OUT'
          AND it.type_id = ev.id
        GROUP BY p.id, p.name;
        :return: quantity of sold out product averaged by week.
        """
        i_ts = self.inventory_transaction_lines
        tot_qty = 0
        max_date, min_date = None, None
        if len(i_ts) > 0:
            for l in i_ts:
                if l.type.code == const.SALES_OUT_INV_TRANS_TYPE_KEY:
                    if l.quantity is not None and l.price is not None:
                        tot_qty += abs(l.quantity)
                    if max_date is None or l.inventory_transaction.date > max_date:
                        max_date = l.inventory_transaction.date
                    if min_date is None or l.inventory_transaction.date < min_date:
                        min_date = l.inventory_transaction.date
        weeks = get_weeks_between(min_date, max_date)
        if weeks == 0:
            weeks = 1
        return format_decimal(tot_qty / weeks)

    @weekly_sold_qty.setter
    def weekly_sold_qty(self, value):
        pass

    @weekly_sold_qty.expression
    def weekly_sold_qty(self):
        from psi.app.models.sales_order import SalesOrderLine, SalesOrder
        return ((select([func.sum(SalesOrderLine.quantity)])
                 .where(self.id == SalesOrderLine.product_id)
                 .where(SalesOrderLine.sales_order_id == SalesOrder.id)
                 .where(SalesOrder.order_date > func.now() - 7)).label('weekly_sold_qty'))

    def cal_inv_trans_average(self, transaction_type):
        i_ts = self.inventory_transaction_lines
        tot_amt = 0
        tot_qty = 0
        if len(i_ts) > 0:
            for l in i_ts:
                if l.type.code == transaction_type:
                    if l.quantity is not None and l.price is not None:
                        tot_qty += abs(l.quantity)
                        tot_amt += abs(l.quantity) * l.price
        if tot_amt != 0 and tot_qty != 0:
            return format_decimal(tot_amt / tot_qty)
        return 0
