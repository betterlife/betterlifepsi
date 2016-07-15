# encoding: utf-8
from decimal import Decimal

from app.service import Info
from app import const
from app.utils.format_util import format_decimal
from app.models.data_security_mixin import DataSecurityMixin
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

db = Info.get_db()


class Shipping(db.Model, DataSecurityMixin):
    __tablename__ = 'shipping'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    remark = Column(Text)

    status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    status = relationship('EnumValues', foreign_keys=[status_id])

    sales_order_id = Column(Integer, ForeignKey('sales_order.id'), nullable=False)
    sales_order = relationship('SalesOrder', backref=backref('so_shipping', uselist=False))

    inventory_transaction_id = Column(Integer, ForeignKey('inventory_transaction.id'), nullable=True)
    inventory_transaction = relationship('InventoryTransaction',
                                         backref=backref('it_shipping', uselist=False, ))

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    @staticmethod
    def status_filter():
        from app.models.enum_values import EnumValues
        return EnumValues.type_filter(const.SHIPPING_STATUS_KEY)

    @hybrid_property
    def total_amount(self):
        return format_decimal(Decimal(sum(line.total_amount for line in self.lines)))

    @total_amount.expression
    def total_amount(self):
        return (select([func.sum(ShippingLine.price * ShippingLine.quantity)])
                .where(self.id == ShippingLine.shipping_id).label('total_amount'))

    @total_amount.setter
    def total_amount(self, value):
        pass

    @staticmethod
    def filter_by_so_id(so_id):
        return Info.get_db().session.query(Shipping).filter_by(sales_order_id=so_id).all()

    def __unicode__(self):
        return str(self.id) + ' - ' + str(self.total_amount)

    def create_or_update_inventory_transaction(self):
        from app.models.inventory_transaction import InventoryTransactionLine, InventoryTransaction
        from app.models.enum_values import EnumValues
        it_type = EnumValues.find_one_by_code(const.SALES_OUT_INV_TRANS_TYPE_KEY)
        it = self.inventory_transaction
        if it is None:
            it = InventoryTransaction()
            it.type = it_type
            self.inventory_transaction = it
        it.date = self.date
        for line in self.lines:
            itl = line.inventory_transaction_line
            if itl is None:
                itl = InventoryTransactionLine()
            itl.quantity = -line.quantity
            itl.product_id = line.product_id
            itl.price = line.price
            itl.in_transit_quantity = 0
            itl.inventory_transaction = it
            line.inventory_transaction_line = itl
        Info.get_db().session.add(it)


class ShippingLine(db.Model):
    __tablename = 'shipping_line'
    id = Column(Integer, primary_key=True)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)

    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product', backref=backref('shipping_lines'))

    shipping_id = Column(Integer, ForeignKey('shipping.id'), nullable=False)
    shipping = relationship('Shipping', backref=backref('lines', uselist=True, cascade='all, delete-orphan'))

    sales_order_line_id = Column(Integer, ForeignKey('sales_order_line.id'), nullable=False)
    sales_order_line = relationship('SalesOrderLine', backref=backref('sol_shipping_line', uselist=False, ))

    inventory_transaction_line_id = Column(Integer, ForeignKey('inventory_transaction_line.id'), nullable=True)
    inventory_transaction_line = relationship('InventoryTransactionLine', backref=backref('itl_shipping_line',
                                                                                          uselist=False, ))

    def __repr__(self):
        return "{0:s}{1:f}个(价格{2:f}元)".format(self.product.name, self.quantity, self.price)

    @hybrid_property
    def total_amount(self):
        if self.quantity is None:
            q = 0
        else:
            q = self.quantity
        return format_decimal(Decimal(self.price * q))

    @total_amount.setter
    def total_amount(self, val):
        pass

    @total_amount.expression
    def total_amount(self):
        return select([self.price * self.quantity]).label('line_total_amount')

    @total_amount.setter
    def total_amount(self, value):
        pass
