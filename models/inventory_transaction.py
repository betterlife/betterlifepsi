# encoding: utf-8
from app_provider import AppInfo
from models import EnumValues
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

    receiving_id = Column(Integer, ForeignKey('receiving.id'), nullable=True)
    receiving = relationship('Receiving', backref=backref('inventory_transaction',
                                                          uselist=False, cascade='all, delete-orphan'))

    @staticmethod
    def type_filter():
        return EnumValues.type_filter('INVENTORY_TRANSACTION_TYPE')

    @hybrid_property
    def total_amount(self):
        return format_decimal(sum(line.total_amount for line in self.lines))

    @total_amount.expression
    def total_amount(self):
        return (select([func.sum(InventoryTransactionLine.price * InventoryTransactionLine.quantity)])
                .where(self.id == InventoryTransactionLine.inventory_transaction_id)
                .label('total_amount'))

    @total_amount.setter
    def total_amount(self, value):
        pass

class InventoryTransactionLine(db.Model):
    __tablename = 'inventory_transaction_line'
    id = Column(Integer, primary_key=True)
    quantity = Column( Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product')
    price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    remark = Column(Text)
    inventory_transaction_id = Column(Integer, ForeignKey('inventory_transaction.id'), nullable=False)
    inventory_transaction = relationship('InventoryTransaction',
                                         backref=backref('lines', cascade='all, delete-orphan'))
    receiving_line_id = Column(Integer, ForeignKey('receiving_line.id'), nullable=True)
    receiving_line = relationship('ReceivingLine',
                                  backref=backref('inventory_transaction_line',
                                                  uselist=False, cascade='all, delete-orphan'))
    sales_order_line_id = Column(Integer, ForeignKey('sales_order_line.id'), nullable=True)
    sales_order_line = relationship('SalesOrderLine',
                                    backref=backref('inventory_transaction_line',
                                                    uselist=False, cascade='all, delete-orphan'))
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
        return format_decimal(self.price * self.quantity)

    @total_amount.expression
    def total_amount(self):
        return select([self.price * self.quantity]).label('line_total_amount')

    @total_amount.setter
    def total_amount(self, value):
        pass