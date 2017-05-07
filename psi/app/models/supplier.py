# encoding: utf-8
from psi.app.service import Info
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, event
from sqlalchemy.orm import backref, relationship

from psi.app.models.data_security_mixin import DataSecurityMixin

db = Info.get_db()


class Supplier(db.Model, DataSecurityMixin):
    __tablename__ = 'supplier'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=False, nullable=False)
    external_id = Column(String(), nullable=True, unique=False)
    qq = Column(String(16))
    phone = Column(String(32))
    contact = Column(String(64))
    email = Column(String(64))
    website = Column(String(64))
    whole_sale_req = Column(String(128))
    can_mixed_whole_sale = Column(Boolean)
    remark = Column(Text)
    mnemonic = Column(String(128), unique=False, nullable=True)

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

class PaymentMethod(db.Model):
    __tablename__ = 'payment_method'
    id = Column(Integer, primary_key=True)
    account_name = Column(String(64), nullable=False)
    account_number = Column(String(64), nullable=False)
    bank_name = Column(String(64), nullable=False)
    bank_branch = Column(String(64))
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier = relationship('Supplier', backref=backref('paymentMethods', cascade='all, delete-orphan'))
    remark = Column(Text)

    def __unicode__(self):
        return "{0} - {1}".format(self.bank_name, self.account_name)
