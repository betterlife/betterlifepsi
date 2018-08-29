# encoding: utf-8
from decimal import Decimal

from psi.app import const
from psi.app.models.data_security_mixin import DataSecurityMixin
from psi.app.service import Info
from psi.app.utils import user_has_role
from psi.app.utils.format_util import format_decimal
from flask_login import current_user
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
        from psi.app.models.enum_values import EnumValues
        return db.session.query(PurchaseOrder) \
            .join(PurchaseOrder.status).filter(EnumValues.code.in_(status_codes))

    @staticmethod
    def status_option_filter():
        from psi.app.models.enum_values import EnumValues
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
        rep = ''
        for e in self.expenses:
            rep += str(e.id) + " - " + str(e.amount) + ", "
        return rep

    @all_expenses.setter
    def all_expenses(self, value):
        pass

    @all_expenses.expression
    def all_expenses(self):
        pass

    @hybrid_property
    def all_receivings(self):
        return ''.join(r.__unicode__() + ", " for r in self.po_receivings)

    @all_receivings.expression
    def all_receivings(self):
        pass

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
        if self.type.code == const.DIRECT_PO_TYPE_KEY:
            s = str(self.supplier.name)
        else:
            s = str(self.organization.name)
        result = "{0}/{1}/{2}/{3}".format(str(self.id), s, str(self.order_date), self.status.display)
        if user_has_role('purchase_price_view'):
            result += "/" + str(self.total_amount)
        return result

    def get_available_lines_info(self):
        # 1. Find all existing receiving bind with this PO.
        from psi.app.models import Receiving
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
                    'price': line.unit_price,
                    'product': line.product,
                }
        else:
            # 3. Calculate un-received line info(qty, price) if there's no existing receiving
            for line in self.lines:
                available_info[line.id] = (line.quantity, line.unit_price)
        return available_info

    @staticmethod
    def all_lines_received(available_info):
        for line_id, line_info in available_info.items():
            if line_info['quantity'] > 0:
                return False
        return True

    @staticmethod
    def create_receiving_lines(available_info):
        from psi.app.models import ReceivingLine
        lines = []
        for line_id, info in available_info.items():
            if info['quantity'] > 0:
                rl = ReceivingLine()
                rl.purchase_order_line_id = line_id
                rl.purchase_order_line, rl.quantity, rl.price, rl.product = \
                    info['line'], info['quantity'], info['price'], info['product']
                lines.append(rl)
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

    def can_delete(self):
        from psi.app.models import EnumValues
        draft_status = EnumValues.get(const.PO_DRAFT_STATUS_KEY)
        return self.status_id == draft_status.id

    def can_edit(self, user=current_user):
        from psi.app.models import EnumValues
        draft_status = EnumValues.get(const.PO_DRAFT_STATUS_KEY)
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
        """
        Query lines by purchase order id
        :param po_id: purchase order id
        :return: list of purchase order lines
        """
        return db.session.query(PurchaseOrderLine).filter_by(purchase_order_id=po_id)

    def __unicode__(self):
        result =  '产品:{0}/数量:{1}'.format(str(self.product.name), str(self.quantity))
        if user_has_role('purchase_price_view'):
            result += "/价格:{0}".format(str(self.unit_price))
        return result
