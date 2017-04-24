# encoding: utf-8
from decimal import Decimal

from datetime import datetime

from psi.app import const
from psi.app.models.data_security_mixin import DataSecurityMixin
from psi.app.service import Info
from psi.app.utils.format_util import format_decimal
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

    type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    type = relationship('EnumValues', foreign_keys=[type_id])

    sales_order_id = Column(Integer, ForeignKey('sales_order.id'), nullable=False)
    sales_order = relationship('SalesOrder', backref=backref('so_shipping', uselist=False))

    inventory_transaction_id = Column(Integer, ForeignKey('inventory_transaction.id'), nullable=True)
    inventory_transaction = relationship('InventoryTransaction',
                                         backref=backref('it_shipping', uselist=False, ))

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    @staticmethod
    def status_filter():
        from psi.app.models.enum_values import EnumValues
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
        from psi.app.models.inventory_transaction import InventoryTransactionLine, InventoryTransaction
        from psi.app.models.enum_values import EnumValues
        if self.type.code == const.DIRECT_SHIPPING_TYPE_KEY:
            it_type = EnumValues.get(const.SALES_OUT_INV_TRANS_TYPE_KEY)
        else:
            it_type = EnumValues.get(const.FRANCHISE_SALES_OUT_INV_TRANS_TYPE_KEY)
        it = self.inventory_transaction
        if it is None:
            it = InventoryTransaction()
            it.type = it_type
            self.inventory_transaction = it
        it.date = self.date
        it.organization = self.organization
        for line in self.lines:
            itl = line.inventory_transaction_line
            if itl is None:
                itl = InventoryTransactionLine()
            itl.quantity = -line.quantity
            itl.product = line.product
            itl.price = line.price
            itl.in_transit_quantity = 0
            itl.inventory_transaction = it
            line.inventory_transaction_line = itl
            self.update_saleable_qty_in_purchase_inv_lines(line)
        Info.get_db().session.add(it)

    def update_saleable_qty_in_purchase_inv_lines(self, ship_line):
        from psi.app.models import InventoryTransactionLine, InventoryInOutLink
        avail_inv_trans = Info.get_db().session.query(InventoryTransactionLine) \
            .filter(InventoryTransactionLine.saleable_quantity > 0,
                    InventoryTransactionLine.product_id == ship_line.product.id) \
            .order_by(InventoryTransactionLine.id).all()
        to_update_purchase_inventory_line, inventory_in_out_links = [],[]
        for recv_iv_trans in avail_inv_trans:
            remain_qty = ship_line.quantity
            if recv_iv_trans.saleable_quantity >= ship_line.quantity:
                recv_iv_trans.saleable_quantity = recv_iv_trans.saleable_quantity \
                                                     - ship_line.quantity
                remain_qty = 0
            else:
                recv_iv_trans.saleable_quantity = 0
                remain_qty = ship_line.quantity \
                                - recv_iv_trans.saleable_quantity
            link = InventoryInOutLink()
            link.date = datetime.now()
            link.product = ship_line.product
            link.in_price = recv_iv_trans.price
            link.in_date = recv_iv_trans.itl_receiving_line.receiving.date
            link.receiving_line_id = recv_iv_trans.itl_receiving_line.id
            link.out_price = ship_line.price
            link.out_date = ship_line.shipping.date
            link.out_quantity = ship_line.quantity
            link.shipping_line = ship_line
            link.organization = ship_line.shipping.organization
            to_update_purchase_inventory_line.append(recv_iv_trans)
            inventory_in_out_links.append(link)
            if remain_qty == 0:
                break
        for l in to_update_purchase_inventory_line:
            Info.get_db().session.add(l)
        for l in inventory_in_out_links:
            Info.get_db().session.add(l)


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
