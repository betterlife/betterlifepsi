# encoding: utf-8
import sys
from decimal import Decimal, ROUND_HALF_UP

from app_provider import AppInfo
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, Text, DateTime, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

reload(sys)
sys.setdefaultencoding("utf-8")

db = AppInfo.get_db()

def format_decimal(value):
    return Decimal(value.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(128), unique=True, nullable=False)
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


class Product(db.Model):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(128), unique=True, nullable=False)
    deliver_day = Column(Integer)
    lead_day = Column(Integer)
    distinguishing_feature = Column(Text)
    spec_link = Column(String(128))
    purchase_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    retail_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
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
    account_name = Column(String(64), nullable=False)
    account_number = Column(String(64), nullable=False)
    bank_name = Column(String(64), nullable=False)
    bank_branch = Column(String(64))
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier = relationship('Supplier', backref=backref('paymentMethods',
                                                        cascade='all, delete-orphan', lazy='dynamic'))
    remark = Column(Text)

    def __unicode__(self):
        return "{0} - {1}".format(self.bank_name, self.account_name)

class SalesOrder(db.Model):
    __tablename__ = 'sales_order'
    id = Column(Integer, primary_key=True)
    logistic_amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    order_date = Column(DateTime, nullable=False)
    remark = Column(Text)

    @hybrid_property
    def actual_amount(self):
        return format_decimal(sum(line.actual_amount for line in self.lines))

    @actual_amount.expression
    def actual_amount(self):
        return (select([func.sum(SalesOrderLine.unit_price * SalesOrderLine.quantity)])
                .where(self.id == SalesOrderLine.sales_order_id).label('actual_amount'))

    @actual_amount.setter
    def actual_amount(self, value):
        pass

    @hybrid_property
    def original_amount(self):
        return format_decimal(sum(line.original_amount for line in self.lines))

    @original_amount.expression
    def original_amount(self):
        return (select([func.sum(SalesOrderLine.original_amount)])
                .where(self.id == SalesOrderLine.sales_order_id)
                .label('original_amount'))

    @original_amount.setter
    def original_amount(self, value):
        pass

    @hybrid_property
    def discount_amount(self):
        return self.original_amount - self.actual_amount

    @discount_amount.setter
    def discount_amount(self, value):
        pass

    def __unicode__(self):
        return str(self.id) + ' - ' + str(self.actual_amount)

class SalesOrderLine(db.Model):
    __tablename__ = 'sales_order_line'
    id = Column(Integer, primary_key=True)
    unit_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)

    sales_order_id = Column(Integer, ForeignKey('sales_order.id'), nullable=False)
    sales_order = relationship('SalesOrder', backref=backref('lines',
                                                             cascade='all, delete-orphan', lazy='dynamic'))

    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product')
    remark = Column(Text)

    @hybrid_property
    def discount_amount(self):
        return format_decimal(self.original_amount - self.actual_amount)

    @discount_amount.setter
    def discount_amount(self, adjust_amount):
        pass

    @hybrid_property
    def actual_amount(self):
        return format_decimal(self.unit_price * self.quantity)

    @actual_amount.expression
    def actual_amount(self):
        return select([self.quantity * self.unit_price]).label('line_actual_amount')

    @actual_amount.setter
    def actual_amount(self, actual_amount):
        pass

    @hybrid_property
    def original_amount(self):
        return format_decimal(self.product.retail_price * self.quantity)

    @original_amount.expression
    def original_amount(self):
        return (select([SalesOrderLine.quantity * Product.retail_price])
                .where(self.product_id == Product.id).label('line_original_amount'))

    @original_amount.setter
    def original_amount(self, original_amount):
        pass

    @hybrid_property
    def price_discount(self):
        return format_decimal(self.product.retail_price - self.unit_price)

    @price_discount.setter
    def price_discount(self, price_adjust):
        pass

    @hybrid_property
    def retail_price(self):
        return self.product.retail_price

    @retail_price.setter
    def retail_price(self, retail_price):
        pass

    def __unicode__(self):
        return str(self.id) + ' - ' + self.product.name

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'
    id = Column(Integer, primary_key=True)
    logistic_amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    order_date = Column(DateTime, nullable=False)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier = relationship('Supplier', backref=backref('purchaseOrders', lazy='dynamic'))
    remark = Column(Text)

    @hybrid_property
    def all_expenses(self):
        return ''.join(str(expense.id) + " - " + str(expense.amount) + ", " for expense in self.expenses)

    @all_expenses.setter
    def all_expenses(self, value):
        pass

    @hybrid_property
    def total_amount(self):
        return format_decimal(self.logistic_amount + self.goods_amount)

    @total_amount.expression
    def total_amount(self):
        return self.goods_amount + self.logistic_amount

    @total_amount.setter
    def total_amount(self, value):
        pass

    @hybrid_property
    def goods_amount(self):
        return format_decimal(sum(line.total_amount for line in self.lines))

    @goods_amount.expression
    def goods_amount(self):
        return (select([func.sum(PurchaseOrderLine.unit_price * PurchaseOrderLine.quantity)])
                .where(self.id == PurchaseOrderLine.purchase_order_id)
                .label('goods_amount'))

    @goods_amount.setter
    def goods_amount(self, value):
        pass

    def __unicode__(self):
        return str(self.id) + ' - ' + str(self.supplier.name)


class PurchaseOrderLine(db.Model):
    __tablename__ = 'purchase_order_line'
    id = Column(Integer, primary_key=True)
    unit_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)

    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=False)
    purchase_order = relationship('PurchaseOrder', backref=backref('lines',
                                                                   cascade='all, delete-orphan', lazy='dynamic'))

    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product')

    remark = Column(Text)

    @hybrid_property
    def total_amount(self):
        return format_decimal(self.unit_price * self.quantity)

    @total_amount.expression
    def total_amount(self):
        return select([self.unit_price * self.quantity]).label('line_total_amount')

    @total_amount.setter
    def total_amount(self, value):
        pass

    def __unicode__(self):
        return str(self.id) + ' - ' + str(self.product.name)


class EnumValues(db.Model):
    __tablename__ = 'enum_values'
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('enum_values.id'))
    type = relationship('EnumValues', remote_side=id,
                        backref=backref('type_values', lazy='dynamic'))
    code = Column(String(32), unique=True, nullable=False)
    display = Column(String(64), nullable=False)

    @staticmethod
    def type_filter(type_code):
        return AppInfo.get_db().session.query(EnumValues).\
            join(EnumValues.type, aliased=True).\
            filter_by(code=type_code)

    def __repr__(self):
        return self.display.encode('utf-8')

    def __unicode__(self):
        return self.display.encode('utf-8')

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
    purchase_order = relationship('PurchaseOrder', backref=backref('expenses',
                                                                   uselist=True, cascade='all, delete-orphan'))
    sales_order_id = Column(Integer, ForeignKey('sales_order.id'))
    sales_order = relationship('SalesOrder', backref=backref('expense',
                                                             uselist=False, cascade='all, delete-orphan'))

    remark = Column(Text)

    def __init__(self, amount=0, exp_date=None, status_id=None, category_id=None):
        self.amount = amount
        self.date = exp_date
        self.status_id = status_id
        self.category_id = category_id
        self.has_invoice = False

    @staticmethod
    def status_filter():
        return EnumValues.type_filter('EXP_STATUS')

    @staticmethod
    def type_filter():
        return EnumValues.type_filter('EXP_TYPE')

    def __unicode__(self):
        return str(self.id) + ' - ' + str(self.amount)

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

class Preference(db.Model):
    __tablename__ = 'preference'
    id = Column(Integer, primary_key=True)
    def_so_incoming_type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_so_incoming_type = relationship('EnumValues', foreign_keys=[def_so_incoming_type_id])
    def_so_incoming_status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_so_incoming_status = relationship('EnumValues', foreign_keys=[def_so_incoming_status_id])

    def_so_exp_type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_so_exp_type = relationship('EnumValues', foreign_keys=[def_so_exp_type_id])
    def_so_exp_status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_so_exp_status = relationship('EnumValues', foreign_keys=[def_so_exp_status_id])

    def_po_logistic_exp_status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_po_logistic_exp_status = relationship('EnumValues', foreign_keys=[def_po_logistic_exp_status_id])
    def_po_logistic_exp_type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_po_logistic_exp_type = relationship('EnumValues', foreign_keys=[def_po_logistic_exp_type_id])

    def_po_goods_exp_status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_po_goods_exp_status = relationship('EnumValues', foreign_keys=[def_po_goods_exp_status_id])
    def_po_goods_exp_type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_po_goods_exp_type = relationship('EnumValues', foreign_keys=[def_po_goods_exp_type_id])

    remark = Column(Text)

    @staticmethod
    def get():
        return Preference.query.get(1)