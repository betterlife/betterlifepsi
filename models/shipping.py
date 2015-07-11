# encoding: utf-8
from decimal import Decimal
from app_provider import AppInfo
from models.util import format_decimal
from models.enum_values import EnumValues
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

db = AppInfo.get_db()


class Shipping(db.Model):
    __tablename__ = 'shipping'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    remark = Column(Text)

    status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    status = relationship('EnumValues', foreign_keys=[status_id])

    sales_order_id = Column(Integer, ForeignKey('sales_order.id'), nullable=False)
    sales_order = relationship('SalesOrder', backref=backref('so_shippings',
                                                             uselist=True, cascade='all, delete-orphan'))

    inventory_transaction_id = Column(Integer, ForeignKey('inventory_transaction.id'), nullable=True)
    inventory_transaction = relationship('InventoryTransaction',
                                         backref=backref('it_shipping', uselist=False,))

    @staticmethod
    def status_filter():
        return EnumValues.type_filter('SHIPPING_STATUS')

    @hybrid_property
    def transient_so(self):
        """
        This design is to display a readonly field containing current
        Purchase order information in UI but don't allow user to change it.
        :return: Current purchase order instance as a transient property
        """
        return self.sales_order

    @transient_so.setter
    def transient_so(self, val):
        pass

    @hybrid_property
    def total_amount(self):
        return format_decimal(Decimal(sum(line.total_amount for line in self.lines)))

    @total_amount.expression
    def total_amount(self):
        return (select([func.sum(ShippingLine.price * ShippingLine.quantity)])
                .where(self.id == Shipping.shipping_id).label('total_amount'))

    @total_amount.setter
    def total_amount(self, value):
        pass

    @staticmethod
    def filter_by_so_id(so_id):
        return AppInfo.get_db().session.query(Shipping).filter_by(sales_order_id=so_id).all()

    def __unicode__(self):
        return str(self.id) + ' - ' + str(self.total_amount)

class ShippingLine(db.Model):
    __tablename = 'shipping_line'
    id = Column(Integer, primary_key=True)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)

    shipping_id = Column(Integer, ForeignKey('shipping.id'), nullable=False)
    shipping = relationship('Shipping', backref=backref('lines', uselist=True, cascade='all, delete-orphan'))

    sales_order_line_id = Column(Integer, ForeignKey('sales_order_line.id'), nullable=False)
    sales_order_line = relationship('SalesOrderLine', backref=backref('sol_shipping_lines',
                                                                      uselist=True, cascade='all, delete-orphan'))

    inventory_transaction_line_id = Column(Integer, ForeignKey('inventory_transaction_line.id'), nullable=True)
    inventory_transaction_line = relationship('InventoryTransactionLine', backref=backref('itl_shipping_line',
                                                                                          uselist=False,))

    @hybrid_property
    def product(self):
        return self.sales_order_line.product

    @product.setter
    def product(self, value):
        pass

    @product.expression
    def product(self):
        return select(self.sales_order_line.product).label('product_id')

    @hybrid_property
    def total_amount(self):
        if self.quantity is None:
            q = 0
        else:
            q = self.quantity
        return format_decimal(Decimal(self.price * q))

    @total_amount.expression
    def total_amount(self):
        return select([self.price * self.quantity]).label('line_total_amount')

    @total_amount.setter
    def total_amount(self, value):
        pass
