# encoding: utf-8
from app_provider import AppInfo
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime
from sqlalchemy.orm import backref, relationship

db = AppInfo.get_db()

class InventoryTransaction(db.Model):
    __tablename__ = 'inventory_transaction'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    type = relationship('EnumValues', foreign_keys=[type_id])
    remark = Column(Text)

class InventoryTransactionLine(db.Model):
    __tablename = 'inventory_transaction_line'
    id = Column(Integer, primary_key=True)
    quantity = Column( Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product')
    price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    remark = Column(Text)
    inventory_transaction_id = Column(Integer, ForeignKey('inventory_transaction.id'))
    inventory_transaction = relationship('InventoryTransaction',
                               backref=backref('lines', uselist=False, cascade='all, delete-orphan'))
