# encoding: utf-8
from decimal import Decimal

from app.app_provider import AppInfo
from util import format_decimal
from product import Product
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

db = AppInfo.get_db()

class SalesOrder(db.Model):
    __tablename__ = 'sales_order'
    id = Column(Integer, primary_key=True)
    logistic_amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    order_date = Column(DateTime, nullable=False)
    remark = Column(Text)

    @hybrid_property
    def actual_amount(self):
        return format_decimal(Decimal(sum(line.actual_amount for line in self.lines)))

    @actual_amount.expression
    def actual_amount(self):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)])
                .where(self.id == SalesOrderLine.sales_order_id).label('actual_amount'))

    @actual_amount.setter
    def actual_amount(self, value):
        pass

    @hybrid_property
    def original_amount(self):
        return format_decimal(Decimal(sum(line.original_amount for line in self.lines)))

    @original_amount.expression
    def original_amount(self):
        return (select([func.sum(SalesOrderLine.original_amount)])
                .where(self.id == SalesOrderLine.sales_order_id)
                .label('original_amount'))

    @original_amount.setter
    def original_amount(self, value):
        pass

    @hybrid_property
    def discount_amount(self):
        return self.original_amount - self.actual_amount

    @discount_amount.setter
    def discount_amount(self, value):
        pass

    @hybrid_property
    def all_shippings(self):
        return self.so_shipping.__unicode__()

    def __unicode__(self):
        return str(self.id) + ' - ' + str(self.actual_amount)

class SalesOrderLine(db.Model):
    __tablename__ = 'sales_order_line'
    id = Column(Integer, primary_key=True)
    unit_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)

    sales_order_id = Column(Integer, ForeignKey('sales_order.id'), nullable=False)
    sales_order = relationship('SalesOrder', backref=backref('lines', cascade='all, delete-orphan'))

    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product')
    remark = Column(Text)

    @hybrid_property
    def discount_amount(self):
        return format_decimal(self.original_amount - self.actual_amount)

    @discount_amount.setter
    def discount_amount(self, adjust_amount):
        pass

    @hybrid_property
    def actual_amount(self):
        return format_decimal(self.unit_price * self.quantity)

    @actual_amount.expression
    def actual_amount(self):
        return select([self.quantity * self.unit_price]).label('line_actual_amount')

    @actual_amount.setter
    def actual_amount(self, actual_amount):
        pass

    @hybrid_property
    def original_amount(self):
        return format_decimal(self.product.retail_price * self.quantity)

    @original_amount.expression
    def original_amount(self):
        return (select([SalesOrderLine.quantity * Product.retail_price])
                .where(self.product_id == Product.id).label('line_original_amount'))

    @original_amount.setter
    def original_amount(self, original_amount):
        pass

    @hybrid_property
    def price_discount(self):
        return format_decimal(self.product.retail_price - self.unit_price)

    @price_discount.setter
    def price_discount(self, price_adjust):
        pass

    @hybrid_property
    def retail_price(self):
        return self.product.retail_price

    @retail_price.setter
    def retail_price(self, retail_price):
        pass

    def __unicode__(self):
        return str(self.id) + ' - ' + self.product.name