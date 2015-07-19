# encoding: utf-8
from decimal import Decimal
from app_provider import AppInfo
import const
from models.enum_values import EnumValues
from util import format_decimal
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

db = AppInfo.get_db()

class InventoryTransaction(db.Model):
    __tablename__ = 'inventory_transaction'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    type = relationship('EnumValues', foreign_keys=[type_id])
    remark = Column(Text)

    @staticmethod
    def type_filter():
        return EnumValues.type_filter(const.INVENTORY_TRANSACTION_TYPE_KEY)

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


class InventoryTransactionLine(db.Model):
    __tablename = 'inventory_transaction_line'
    id = Column(Integer, primary_key=True)
    in_transit_quantity = Column( Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=True)
    quantity = Column( Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product', backref=backref('inventory_transaction_lines'))
    price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
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
        if self.quantity is None:
            q = 0
        else:
            q = self.quantity
        if self.in_transit_quantity is None:
            i_t_q = 0
        else:
            i_t_q = self.in_transit_quantity
        return format_decimal(Decimal(abs(self.price * (q + i_t_q))))

    @total_amount.expression
    def total_amount(self):
        return select([self.price * (self.quantity + self.in_transit_quantity)])\
            .label('line_total_amount')

    @total_amount.setter
    def total_amount(self, value):
        pass
