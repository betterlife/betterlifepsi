# encoding: utf-8
from decimal import Decimal

from flask.ext.login import current_user

from app.service import Info
from app import const
from app.utils.format_util import format_decimal
from app.models.data_security_mixin import DataSecurityMixin
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

db = Info.get_db()


class PurchaseOrder(db.Model, DataSecurityMixin):
    __tablename__ = 'purchase_order'
    id = Column(Integer, primary_key=True)
    logistic_amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    order_date = Column(DateTime, nullable=False)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=True)
    supplier = relationship('Supplier', backref=backref('purchaseOrders', lazy='dynamic'))

    status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    status = relationship('EnumValues', foreign_keys=[status_id])

    type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    type = relationship('EnumValues', foreign_keys=[type_id])

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    to_organization_id = db.Column(Integer, ForeignKey('organization.id'), nullable=True)
    to_organization = relationship('Organization', foreign_keys=[to_organization_id])

    @staticmethod
    def status_filter(status_codes):
        from app.models.enum_values import EnumValues
        return db.session.query(PurchaseOrder) \
            .join(EnumValues).filter(EnumValues.code.in_(status_codes))

    @staticmethod
    def status_option_filter():
        from app.models.enum_values import EnumValues
        return EnumValues.type_filter(const.PO_STATUS_KEY)

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
    def all_receivings(self):
        return ''.join(r.__unicode__() + ", " for r in self.po_receivings)

    @all_receivings.setter
    def all_receivings(self, value):
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
        return str(self.id) + ' - ' + str(self.supplier.name) + ' - ' + str(self.order_date) + ' - ' + str(self.total_amount) + ' - ' + self.status.display

    def get_available_lines_info(self):
        # 1. Find all existing receiving bind with this PO.
        from app.models import Receiving
        existing_res = Receiving.filter_by_po_id(self.id)
        available_info = {}
        if existing_res is not None:
            # 2. Calculate all received line and corresponding qty.
            received_qtys = self.get_received_quantities(existing_res)
            # 3. Calculate all un-received line and corresponding qty
            for line in self.lines:
                quantity = line.quantity
                if line.id in received_qtys.keys():
                    quantity -= received_qtys[line.id]
                available_info[line.id] = {
                    'line': line, 'quantity': quantity,
                    'price': line.unit_price, 'product_id': line.product_id
                }
        else:
            # 3. Calculate un-received line info(qty, price) if there's no existing receiving
            for line in self.lines:
                available_info[line.id] = (line.quantity, line.unit_price)
        return available_info

    @staticmethod
    def all_lines_received(available_info):
        for line_id, line_info in available_info.iteritems():
            if line_info['quantity'] > 0:
                return False
        return True

    @staticmethod
    def create_receiving_lines(available_info):
        from app.models import ReceivingLine
        lines = []
        for line_id, info in available_info.iteritems():
            if info['quantity'] > 0:
                r_line = ReceivingLine()
                r_line.purchase_order_line_id = line_id
                r_line.purchase_order_line, r_line.quantity, r_line.price, r_line.product_id = \
                    info['line'], info['quantity'], info['price'], info['product_id']
                lines.append(r_line)
        return lines

    @staticmethod
    def get_received_quantities(existing_res):
        received_qtys = {}
        for re in existing_res:
            if re.lines is not None and len(re.lines) > 0:
                for line in re.lines:
                    line_no = line.purchase_order_line_id
                    received_qty = None
                    if line_no in received_qtys.keys():
                        received_qty = received_qtys[line_no]
                    if received_qty is None:
                        received_qty = line.quantity
                    else:
                        received_qty += line.quantity
                    received_qtys[line_no] = received_qty
        return received_qtys

    def create_expenses(self):
        """
        Create expense from purchase order
        Create one record for the goods amount, one record for logistic amount
        :return: The logistic expense and goods expense
        """
        from app.models import Expense, Preference
        expenses = self.expenses
        logistic_exp = None
        preference = Preference.get()
        goods_exp = None
        if expenses is None:
            expenses = dict()
        for expense in expenses:
            if (expense.category_id == preference.def_po_logistic_exp_type_id) and (self.logistic_amount != 0):
                logistic_exp = expense
                logistic_exp.amount = self.logistic_amount
            elif (expense.category_id == preference.def_po_goods_exp_type_id) and (self.goods_amount != 0):
                goods_exp = expense
                goods_exp.amount = self.goods_amount
        if (logistic_exp is None) and (self.logistic_amount is not None and self.logistic_amount != 0):
            logistic_exp = Expense(self.logistic_amount, self.order_date,
                                   preference.def_po_logistic_exp_status_id,
                                   preference.def_po_logistic_exp_type_id)
        if (goods_exp is None) and (self.goods_amount is not None and self.goods_amount != 0):
            goods_exp = Expense(self.goods_amount, self.order_date,
                                preference.def_po_goods_exp_status_id,
                                preference.def_po_goods_exp_type_id)
        if logistic_exp is not None:
            logistic_exp.purchase_order_id = self.id
            logistic_exp.organization = self.organization
        if goods_exp is not None:
            goods_exp.purchase_order_id = self.id
            goods_exp.organization = self.organization
        return logistic_exp, goods_exp

    def create_receiving_if_not_exist(self):
        """
        Draft receiving document is created from purchase order only
         if there's no associated receiving exists for this PO.
        :param model: the Purchase order model
        :return: Receiving document if a new one created, or None
        """
        from app.models import Receiving
        receivings = self.po_receivings
        if receivings is None or len(receivings) == 0:
            recv = Receiving.create_draft_recv_from_po(self)
            return recv
        return None

    def can_delete(self):
        from app.models import EnumValues
        draft_status = EnumValues.find_one_by_code(const.PO_DRAFT_STATUS_KEY)
        return self.status_id == draft_status.id

    def can_edit(self, user=current_user):
        from app.models import EnumValues
        draft_status = EnumValues.find_one_by_code(const.PO_DRAFT_STATUS_KEY)
        return self.status_id == draft_status.id


class PurchaseOrderLine(db.Model):
    __tablename__ = 'purchase_order_line'
    id = Column(Integer, primary_key=True)
    unit_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)

    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=False)
    purchase_order = relationship('PurchaseOrder', backref=backref('lines', cascade='all, delete-orphan'))

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
        return db.session.query(PurchaseOrderLine).filter_by(purchase_order_id=po_id)

    def __unicode__(self):
        return 'H:' + str(self.purchase_order_id) + \
               ' - L:' + str(self.id) + ' - N:' + str(self.product.name) + \
               ' - Q:' + str(self.quantity) + ' - P:' + str(self.unit_price)
