# encoding: utf-8
from decimal import Decimal
from app_provider import AppInfo
from models.enum_values import EnumValues
from util import format_decimal
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

db = AppInfo.get_db()

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'
    id = Column(Integer, primary_key=True)
    logistic_amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    order_date = Column(DateTime, nullable=False)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier = relationship('Supplier', backref=backref('purchaseOrders', lazy='dynamic'))

    status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    status = relationship('EnumValues', foreign_keys=[status_id])

    @staticmethod
    def status_filter(status_codes):
        return AppInfo.get_db().session.query(PurchaseOrder)\
            .join(EnumValues).filter(EnumValues.code.in_(status_codes))

    @staticmethod
    def status_option_filter():
        return EnumValues.type_filter('PURCHASE_ORDER_STATUS')

    remark = Column(Text)

    @hybrid_property
    def transient_supplier(self):
        """
        This design is to display a readonly field containing current
        Supplier information in UI but don't allow user to change it.
        :return: Current supplier instance as a transient property
        """
        return self.supplier

    @transient_supplier.setter
    def transient_supplier(self, val):
        pass

    @hybrid_property
    def all_expenses(self):
        return ''.join(str(expense.id) + " - " + str(expense.amount) + ", " for expense in self.expenses)

    @all_expenses.setter
    def all_expenses(self, value):
        pass

    @hybrid_property
    def total_amount(self):
        if self.logistic_amount is None:
            l_a = 0
        else:
            l_a = self.logistic_amount
        if self.goods_amount is None:
            g_a = 0
        else:
            g_a = self.goods_amount
        return format_decimal(Decimal(l_a + g_a))

    @total_amount.expression
    def total_amount(self):
        return self.goods_amount + self.logistic_amount

    @total_amount.setter
    def total_amount(self, value):
        pass

    @hybrid_property
    def goods_amount(self):
        return format_decimal(Decimal(sum(line.total_amount for line in self.lines)))

    @goods_amount.expression
    def goods_amount(self):
        return (select([func.sum(PurchaseOrderLine.unit_price * PurchaseOrderLine.quantity)])
                .where(self.id == PurchaseOrderLine.purchase_order_id)
                .label('goods_amount'))

    @goods_amount.setter
    def goods_amount(self, value):
        pass

    def __unicode__(self):
        return str(self.id) + \
               ' - ' + str(self.supplier.name) + \
               ' - ' + str(self.total_amount) + \
               ' - ' + self.status.display


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

    @staticmethod
    def header_filter(po_id):
        return AppInfo.get_db().session.query(PurchaseOrderLine).filter_by(purchase_order_id=po_id)

    def __unicode__(self):
        return 'H:' + str(self.purchase_order_id) + \
               ' - L:' + str(self.id) + ' - N:' + str(self.product.name) + \
               ' - Q:' + str(self.quantity) + ' - P:' + str(self.unit_price)


