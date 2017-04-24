# encoding: utf-8
from psi.app import const
from psi.app.models.data_security_mixin import DataSecurityMixin
from psi.app.service import Info
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime
from sqlalchemy.orm import backref, relationship

db = Info.get_db()


class Incoming(db.Model, DataSecurityMixin):
    __tablename__ = 'incoming'
    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    date = Column(DateTime, nullable=False)

    category_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    category = relationship('EnumValues', foreign_keys=[category_id])

    status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    status = relationship('EnumValues', foreign_keys=[status_id])

    sales_order_id = Column(Integer, ForeignKey('sales_order.id'))
    sales_order = relationship('SalesOrder', backref=backref('incoming', uselist=False, cascade='all, delete-orphan'))

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    remark = Column(Text)

    @staticmethod
    def status_filter():
        from psi.app.models.enum_values import EnumValues
        return EnumValues.type_filter(const.INCOMING_STATUS_KEY)

    @staticmethod
    def type_filter():
        from psi.app.models.enum_values import EnumValues
        return EnumValues.type_filter(const.INCOMING_TYPE_KEY)

    def __unicode__(self):
        if self.amount is not None:
            return str(self.id) + ' - ' + str(self.amount)
        return str(self.id) + ' - ' + str(0)
