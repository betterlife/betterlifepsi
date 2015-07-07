# encoding: utf-8
from app_provider import AppInfo
from models.enum_values import EnumValues
from models.purchase_order import PurchaseOrderLine
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime
from sqlalchemy.orm import backref, relationship

db = AppInfo.get_db()
class Receiving(db.Model):
    __tablename__ = 'receiving'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    remark = Column(Text)

    status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    status = relationship('EnumValues', foreign_keys=[status_id])

    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=False)
    purchase_order = relationship('PurchaseOrder', backref=backref('inventory_transactions',
                                                                   uselist=True, cascade='all, delete-orphan'))

    @staticmethod
    def status_filter():
        return EnumValues.type_filter('RECEIVING_STATUS')

class ReceivingLine(db.Model):
    __tablename = 'receiving_line'
    id = Column(Integer, primary_key=True)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product')
    price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)

    receiving_id = Column(Integer, ForeignKey('receiving.id'), nullable=False)
    receiving = relationship('Receiving', backref=backref('lines', uselist=True, cascade='all, delete-orphan'))

    purchase_order_line_id = Column(Integer, ForeignKey('purchase_order_line.id'), nullable=False)
    purchase_order_line = relationship('PurchaseOrderLine',
                                       backref=backref('inventory_transaction_lines',
                                                       uselist=True, cascade='all, delete-orphan'))