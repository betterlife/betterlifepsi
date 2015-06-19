# encoding: utf-8
from app_provider import AppInfo
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, Text, DateTime
from sqlalchemy.orm import backref, relationship

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

db = AppInfo.get_db()

class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(32), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('product_category.id'))
    parent_category = relationship('ProductCategory', remote_side=id,
                                   backref=backref('sub_categories', lazy='dynamic'))

    def __unicode__(self):
        return self.code.encode('utf-8') + " - " + self.name.encode('utf-8')

    def __repr__(self):
        return self.code.encode('utf-8') + " - " + self.name.encode('utf-8')


class Supplier(db.Model):
    __tablename__ = 'supplier'
    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(32), unique=True, nullable=False)
    qq = Column(String(16))
    phone = Column(String(32))
    contact = Column(String(16))
    email = Column(String(64))
    website = Column(String(64))
    whole_sale_req = Column(String(32))
    can_mixed_whole_sale = Column(Boolean)
    remark = Column(Text)

    def __unicode__(self):
        return self.name


class Product(db.Model):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(32), unique=True, nullable=False)
    deliver_day = Column(Integer)
    lead_day = Column(Integer)
    distinguishing_feature = Column(Text)
    spec_link = Column(String(64))
    purchase_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    retail_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    category_id = Column(Integer, ForeignKey('product_category.id'), nullable=False)
    category = relationship('ProductCategory', backref=backref('products', lazy='dynamic'))
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier = relationship('Supplier', backref=backref('products', lazy='dynamic'))

    def __unicode__(self):
        return self.code + " - " + self.name

    def __repr__(self):
        return self.__unicode__


class PaymentMethod(db.Model):
    __tablename__ = 'payment_method'
    id = Column(Integer, primary_key=True)
    account_name = Column(String(8), nullable=False)
    account_number = Column(String(32), nullable=False)
    bank_name = Column(String(16), nullable=False)
    bank_branch = Column(String(32))
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier = relationship('Supplier', backref=backref('paymentMethods', lazy='dynamic'))
    remark = Column(Text)

    def __unicode__(self):
        return "{0} - {1}".format(self.bank_name, self.account_name)

class SalesOrder(db.Model):
    __tablename__ = 'sales_order'
    id = Column(Integer, primary_key=True)
    logistic_amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    order_date = Column(DateTime, nullable=False)
    remark = Column(Text)

    def __unicode__(self):
        return self.id

class SalesOrderLine(db.Model):
    __tablename__ = 'sales_order_line'
    id = Column(Integer, primary_key=True)
    unit_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    original_amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    adjust_amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    actual_amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))

    sales_order_id = Column(Integer, ForeignKey('sales_order.id'), nullable=False)
    sales_order = relationship('SalesOrder', backref=backref('lines', lazy='dynamic'))

    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product')
    remark = Column(Text)

    def __unicode__(self):
        return self.id

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'
    id = Column(Integer, primary_key=True)
    logistic_amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    other_amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    order_date = Column(DateTime, nullable=False)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier = relationship('Supplier', backref=backref('purchaseOrders', lazy='dynamic'))
    remark = Column(Text)

    def __unicode__(self):
        return self.id


class PurchaseOrderLine(db.Model):
    __tablename__ = 'purchase_order_line'
    id = Column(Integer, primary_key=True)
    unit_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)

    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=False)
    purchase_order = relationship('PurchaseOrder', backref=backref('lines', lazy='dynamic'))

    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product')

    remark = Column(Text)

    def __unicode__(self):
        return self.id

class EnumValues(db.Model):
    __tablename__ = 'enum_values'
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('enum_values.id'))
    type = relationship('EnumValues', remote_side=id,
                        backref=backref('type_values', lazy='dynamic'))
    code = Column(String(16), unique=True)
    display = Column(String(16), nullable=False)

    @staticmethod
    def type_filter(type_code):
        return AppInfo.get_db().session.query(EnumValues).\
            join(EnumValues.type, aliased=True).\
            filter_by(code=type_code)

    def __unicode__(self):
        return self.display

class Expense(db.Model):
    __tablename__ = 'expense'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    has_invoice = Column(Boolean)

    status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    status = relationship('EnumValues', foreign_keys=[status_id])

    category_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    category = relationship('EnumValues', foreign_keys=[category_id])

    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'))
    sales_order_id = Column(Integer, ForeignKey('sales_order.id'))
    remark = Column(Text)

    @staticmethod
    def status_filter():
        return EnumValues.type_filter('EXP_STATUS')

    @staticmethod
    def type_filter():
        return EnumValues.type_filter('EXP_TYPE')


    def __unicode__(self):
        return self.id

class Incoming(db.Model):
    __tablename__ = 'incoming'
    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    cate = Column(DateTime, nullable=False)

    category_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    category = relationship('EnumValues', foreign_keys=[category_id])

    status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    status = relationship('EnumValues', foreign_keys=[status_id])

    sales_order_id = Column(Integer, ForeignKey('sales_order.id'))
    remark = Column(Text)

    @staticmethod
    def status_filter():
        return EnumValues.type_filter('INCOMING_STATUS')

    @staticmethod
    def type_filter():
        return EnumValues.type_filter('INCOMING_TYPE')

    def __unicode__(self):
        return self.id
