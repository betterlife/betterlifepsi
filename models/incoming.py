# encoding: utf-8
from app_provider import AppInfo
from models.enum_values import EnumValues
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime
from sqlalchemy.orm import backref, relationship

db = AppInfo.get_db()

class Incoming(db.Model):
    __tablename__ = 'incoming'
    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    date = Column(DateTime, nullable=False)

    category_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    category = relationship('EnumValues', foreign_keys=[category_id])

    status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    status = relationship('EnumValues', foreign_keys=[status_id])

    sales_order_id = Column(Integer, ForeignKey('sales_order.id'))
    sales_order = relationship('SalesOrder', backref=backref('incoming',
                                                             uselist=False, cascade='all, delete-orphan'))

    remark = Column(Text)

    @staticmethod
    def status_filter():
        return EnumValues.type_filter('INCOMING_STATUS')

    @staticmethod
    def type_filter():
        return EnumValues.type_filter('INCOMING_TYPE')

    def __unicode__(self):
        if self.amount is not None:
            return str(self.id) + ' - ' + str(self.amount)
        return str(self.id) + ' - ' + str(0)
