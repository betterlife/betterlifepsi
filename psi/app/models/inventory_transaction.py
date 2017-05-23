# encoding: utf-8
from decimal import Decimal

from flask_login import current_user

from psi.app import const
from psi.app.models.data_security_mixin import DataSecurityMixin
from psi.app.service import Info
from psi.app.utils.format_util import format_decimal
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

db = Info.get_db()


class InventoryTransaction(db.Model, DataSecurityMixin):
    __tablename__ = 'inventory_transaction'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    type = relationship('EnumValues', foreign_keys=[type_id])

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    remark = Column(Text)

    @staticmethod
    def type_filter():
        from psi.app.models.enum_values import EnumValues
        return EnumValues.type_filter(const.INVENTORY_TRANSACTION_TYPE_KEY)

    @staticmethod
    def manual_type_filter():
        from psi.app.models.enum_values import EnumValues
        from sqlalchemy import or_
        q = db.session.query(EnumValues).filter(or_(EnumValues.code == const.INVENTORY_LOST_TYPE_KEY,
                                                    EnumValues.code == const.INVENTORY_DAMAGED_TYPE_KEY))
        return q

    @hybrid_property
    def total_amount(self):
        return format_decimal(Decimal(abs(sum(line.total_amount for line in self.lines))))

    @total_amount.expression
    def total_amount(self):
        return (select([func.sum(InventoryTransactionLine.price
                                 * (InventoryTransactionLine.in_transit_quantity
                                    + InventoryTransactionLine.quantity))])
                .where(self.id == InventoryTransactionLine.inventory_transaction_id)
                .label('total_amount'))

    @total_amount.setter
    def total_amount(self, value):
        pass

    def __unicode__(self):
        return str(self.id)

    def can_edit(self, user=current_user):
        return (self.type.code == const.INVENTORY_LOST_TYPE_KEY
               or self.type.code == const.INVENTORY_DAMAGED_TYPE_KEY)


class InventoryTransactionLine(db.Model):
    __tablename = 'inventory_transaction_line'
    id = Column(Integer, primary_key=True)
    in_transit_quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=True)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product', backref=backref('inventory_transaction_lines'))
    price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    saleable_quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=True)
    remark = Column(Text)
    inventory_transaction_id = Column(Integer, ForeignKey('inventory_transaction.id'), nullable=False)
    inventory_transaction = relationship('InventoryTransaction',
                                         backref=backref('lines', cascade='all, delete-orphan'))

    @hybrid_property
    def type(self):
        return self.inventory_transaction.type

    @type.setter
    def type(self, value):
        pass

    @hybrid_property
    def date(self):
        return self.inventory_transaction.date

    @date.setter
    def date(self, value):
        pass

    @hybrid_property
    def total_amount(self):
        q = 0 if self.quantity is None else self.quantity
        i_t_q = 0 if self.in_transit_quantity is None else self.in_transit_quantity
        return format_decimal(Decimal(abs(self.price * (q + i_t_q))))

    @total_amount.expression
    def total_amount(self):
        return select([self.price * (self.quantity + self.in_transit_quantity)]).label('line_total_amount')

    @total_amount.setter
    def total_amount(self, value):
        pass
