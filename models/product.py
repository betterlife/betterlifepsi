# encoding: utf-8
from advice import InventoryAdvice
from app_provider import AppInfo
import const
from enum_values import EnumValues
from models.util import format_decimal, get_weeks_between
from models.inventory_transaction import InventoryTransactionLine, InventoryTransaction
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Text, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

db = AppInfo.get_db()


class Product(db.Model):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(128), unique=True, nullable=False)
    deliver_day = Column(Integer, nullable=False)
    lead_day = Column(Integer, nullable=False)
    distinguishing_feature = Column(Text)
    spec_link = Column(String(128))
    purchase_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    retail_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    category_id = Column(Integer, ForeignKey('product_category.id'), nullable=False)
    category = relationship('ProductCategory', backref=backref('products', lazy='dynamic'))
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier = relationship('Supplier', backref=backref('products', lazy='dynamic'))

    @hybrid_property
    def in_transit_quantity(self):
        i_ts = self.inventory_transaction_lines
        total = 0
        if len(i_ts) > 0:
            for l in i_ts:
                if l.in_transit_quantity is not None:
                    total += l.in_transit_quantity
        return total

    @in_transit_quantity.setter
    def in_transit_quantity(self, val):
        pass

    @in_transit_quantity.expression
    def in_transit_quantity(self):
        return (select([func.sum(InventoryTransactionLine.in_transit_quantity)])
                .where(self.id == InventoryTransactionLine.product_id)
                .label('in_transit_stock'))

    @hybrid_property
    def available_quantity(self):
        i_ts = self.inventory_transaction_lines
        total = 0
        if len(i_ts) > 0:
            for l in i_ts:
                if l.quantity is not None:
                    total += l.quantity
        return total

    @available_quantity.setter
    def available_quantity(self, val):
        pass

    @available_quantity.expression
    def available_quantity(self):
        return (select([func.sum(InventoryTransactionLine.quantity)])
                .where(self.id == InventoryTransactionLine.product_id)
                .label('available_quantity'))

    @hybrid_property
    def average_purchase_price(self):
        return self.cal_inv_trans_average(const.PURCHASE_IN_INV_TRANS_KEY)

    @average_purchase_price.setter
    def average_purchase_price(self, val):
        pass

    @average_purchase_price.expression
    def average_purchase_price(self):
        from models import EnumValues
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
        from models import EnumValues
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
        return (select([-func.sum(InventoryTransactionLine.quantity * InventoryTransactionLine.price) /
                        func.greatest(func.sum(InventoryTransactionLine.quantity), 1)])
                .where(self.id == InventoryTransactionLine.product_id
                       and InventoryTransactionLine.inventory_transaction_id == InventoryTransaction.id
                       and InventoryTransaction.type_id == EnumValues.id
                       and (EnumValues.code == const.SALES_OUT_INV_TRANS_TYPE_KEY or
                            EnumValues.code == const.PURCHASE_IN_INV_TRANS_KEY)))\
            .label('average_unit_profit')

    @hybrid_property
    def weekly_average_profit(self):
        if 0 == self.average_unit_profit:
            return 0
        return format_decimal(self.weekly_sold_qty * self.average_unit_profit)

    @weekly_average_profit.setter
    def weekly_average_profit(self, value):
        pass

    @hybrid_property
    def inventory_advice(self):
            return InventoryAdvice.advice(self)

    @inventory_advice.setter
    def inventory_advice(self, value):
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

    @staticmethod
    def supplier_filter(s_id):
        return AppInfo.get_db().session.query(Product).filter_by(supplier_id=s_id)

    def get_lead_deliver_day(self):
        if self.deliver_day is None and self.lead_day is None:
            return 0
        elif self.deliver_day is None:
            return self.lead_day
        elif self.lead_day is None:
            return self.deliver_day
        return self.deliver_day + self.lead_day

    def get_profit_lost_caused_by_inventory_short(self):
        if self.average_unit_profit == 0 or self.weekly_sold_qty == 0:
            return 0
        can_sell_day = format_decimal(self.available_quantity / self.weekly_sold_qty)
        days_without_prd = (self.get_lead_deliver_day() - can_sell_day)
        return self.average_unit_profit * self.weekly_sold_qty * days_without_prd / 7

    def __unicode__(self):
        return self.supplier.name + ' - ' + self.name + ' - P:' \
               + str(self.purchase_price) + ' - R:' + str(self.retail_price)

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return self.name
