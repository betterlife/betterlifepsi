# encoding: utf-8
from app_provider import AppInfo
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import backref, relationship

db = AppInfo.get_db()

class Supplier(db.Model):
    __tablename__ = 'supplier'
    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(128), unique=True, nullable=False)
    qq = Column(String(16))
    phone = Column(String(32))
    contact = Column(String(64))
    email = Column(String(64))
    website = Column(String(64))
    whole_sale_req = Column(String(128))
    can_mixed_whole_sale = Column(Boolean)
    remark = Column(Text)

    def __unicode__(self):
        return self.name

class PaymentMethod(db.Model):
    __tablename__ = 'payment_method'
    id = Column(Integer, primary_key=True)
    account_name = Column(String(64), nullable=False)
    account_number = Column(String(64), nullable=False)
    bank_name = Column(String(64), nullable=False)
    bank_branch = Column(String(64))
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier = relationship('Supplier',
                            backref=backref('paymentMethods',
                                            cascade='all, delete-orphan', lazy='dynamic'))
    remark = Column(Text)

    def __unicode__(self):
        return "{0} - {1}".format(self.bank_name, self.account_name)