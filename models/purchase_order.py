# encoding: utf-8
from app_provider import AppInfo
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
        return str(self.id) + ' - ' + str(self.supplier.name) + ' - ' + str(self.total_amount)


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
        return 'H:' + str(self.purchase_order_id) + ' - L:' + str(self.id) + ' - ' + str(self.product.name) + \
               ' - P:' + str(self.unit_price) + ' - Q:' + str(self.quantity)


