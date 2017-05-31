# encoding: utf-8
from decimal import Decimal

from psi.app import const
from psi.app.service import Info
from psi.app.utils.format_util import format_decimal
from flask_login import current_user
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime, select, func, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

from psi.app.models.data_security_mixin import DataSecurityMixin

db = Info.get_db()


class SalesOrder(db.Model, DataSecurityMixin):
    __tablename__ = 'sales_order'
    id = Column(Integer, primary_key=True)
    logistic_amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    order_date = Column(DateTime, nullable=False)
    external_id = Column(String(), nullable=True, unique=False)

    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    customer = relationship('Customer', foreign_keys=[customer_id], backref=backref('sales_orders', uselist=True))

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    type = relationship('EnumValues', foreign_keys=[type_id])

    status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    status = relationship('EnumValues', foreign_keys=[status_id])

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

    def __unicode__(self):
        return str(self.id) + ' - ' + str(self.actual_amount)

    def can_delete(self):
        can = super(SalesOrder, self).can_delete()
        return (can and self.status.code == const.SO_CREATED_STATUS_KEY
                and self.type.code != const.FRANCHISE_SO_TYPE_KEY)

    def can_edit(self, user=current_user):
        can = super(SalesOrder, self).can_edit()
        return can and self.status.code != const.SO_DELIVERED_STATUS_KEY

    @staticmethod
    def status_option_filter():
        from psi.app.models.enum_values import EnumValues
        return EnumValues.type_filter(const.SO_STATUS_KEY)


class SalesOrderLine(db.Model):
    __tablename__ = 'sales_order_line'
    id = Column(Integer, primary_key=True)
    unit_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)

    sales_order_id = Column(Integer, ForeignKey('sales_order.id'), nullable=False)
    sales_order = relationship('SalesOrder', backref=backref('lines', cascade='all, delete-orphan'))

    external_id = Column(String(), nullable=True)

    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product', backref=backref('sales_order_lines'))
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
        from psi.app.models.product import Product
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

    @hybrid_property
    def transient_external_id(self):
        """
        This design is to display a readonly field containing current
        external id information in UI but don't allow user to change it.
        :return: Current external id as a transient property
        """
        return self.external_id

    @transient_external_id.setter
    def transient_external_id(self, val):
        pass

    def __unicode__(self):
        return str(self.id) + ' - ' + self.product.name
