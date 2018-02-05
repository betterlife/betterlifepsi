# encoding: utf-8
from decimal import Decimal

from flask import flash
from flask_babelex import gettext
from flask_login import current_user

from psi.app import const
from psi.app.models.data_security_mixin import DataSecurityMixin
from psi.app.service import Info
from psi.app.utils.format_util import format_decimal
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

db = Info.get_db()


class Receiving(db.Model, DataSecurityMixin):
    __tablename__ = 'receiving'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    remark = Column(Text)

    status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    status = relationship('EnumValues', foreign_keys=[status_id])

    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=False)
    purchase_order = relationship('PurchaseOrder', backref=backref('po_receivings', uselist=True, ))

    inventory_transaction_id = Column(Integer, ForeignKey('inventory_transaction.id'), nullable=True)
    inventory_transaction = relationship('InventoryTransaction', backref=backref('it_receiving', uselist=False, cascade='all, delete-orphan'))

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    @staticmethod
    def status_filter():
        from psi.app.models.enum_values import EnumValues
        return EnumValues.type_filter(const.RECEIVING_STATUS_KEY)

    @hybrid_property
    def transient_po(self):
        """
        This design is to display a readonly field containing current
        Purchase order information in UI but don't allow user to change it.
        :return: Current purchase order instance as a transient property
        """
        return self.purchase_order

    @transient_po.setter
    def transient_po(self, val):
        pass

    @hybrid_property
    def supplier(self):
        return self.purchase_order.supplier

    @supplier.setter
    def supplier(self, val):
        pass

    @hybrid_property
    def total_amount(self):
        return format_decimal(Decimal(sum(line.total_amount for line in self.lines)))

    @total_amount.expression
    def total_amount(self):
        return (select([func.sum(ReceivingLine.price * ReceivingLine.quantity)])
                .where(self.id == ReceivingLine.receiving_id).label('total_amount'))

    @total_amount.setter
    def total_amount(self, value):
        pass

    def __repr__(self):
        po_id = str(self.purchase_order_id)
        if self.supplier is not None:
            return u"采购单: " + po_id + u", 供应商: " + self.supplier.name + u", 日期: " + self.date.strftime("%Y/%m/%d")
        return u"采购单: " + po_id + u", 日期: " + self.date.strftime("%Y/%m/%d")

    def __unicode__(self):
        return self.__repr__()

    @staticmethod
    def filter_by_po_id(po_id):
        return Info.get_db().session.query(Receiving).filter_by(purchase_order_id=po_id).all()

    @staticmethod
    def create_draft_recv_from_po(po):
        from psi.app.models.enum_values import EnumValues
        recv_draft_status = EnumValues.get(const.RECEIVING_DRAFT_STATUS_KEY)
        purchase_in_trans_type = EnumValues.get(const.PURCHASE_IN_INV_TRANS_KEY)
        recv = Receiving()
        recv.purchase_order = po
        recv.date = po.order_date
        recv.organization = po.organization
        recv.status = recv_draft_status
        recv.supplier = po.supplier
        from psi.app.models import InventoryTransaction
        trans = InventoryTransaction()
        trans.date = recv.date
        trans.type = purchase_in_trans_type
        trans.organization = po.organization
        recv.inventory_transaction = trans
        for line in po.lines:
            recv_l = ReceivingLine()
            recv_l.receiving = recv
            recv_l.price = line.unit_price
            recv_l.product = line.product
            recv_l.quantity = line.quantity
            recv_l.purchase_order_line = line
            from psi.app.models import InventoryTransactionLine
            trans_l = InventoryTransactionLine()
            trans_l.price = recv_l.price
            trans_l.in_transit_quantity = recv_l.quantity
            trans_l.product = recv_l.product
            trans_l.quantity = 0
            trans_l.inventory_transaction = trans
            recv_l.inventory_transaction_line = trans_l
        return recv

    def update_purchase_order_status(self):
        """
        Update related purchase order's status based on received qty status
        For each line, if received >= line quantity, assume this line is finish
         If all lines are finished, set status of the purchase order to received
         Otherwise set the status to partially received.
        """
        from psi.app.models import EnumValues
        if self.status.code == const.RECEIVING_COMPLETE_STATUS_KEY:
            po = self.purchase_order
            not_finished,started = False, False
            for line in po.lines:
                receiving_lines = line.pol_receiving_lines
                rd_qty = 0
                for rl in receiving_lines:
                    rd_qty += rl.quantity
                if rd_qty > 0:
                    started = True
                if rd_qty < line.quantity:
                    not_finished = True
            if not_finished is False:
                po.status = EnumValues.get(const.PO_RECEIVED_STATUS_KEY)
            elif started is True:
                po.status = EnumValues.get(const.PO_PART_RECEIVED_STATUS_KEY)
            db.session.add(po)
            return po

    def operate_inv_trans_by_recv_status(self):
        inv_trans = None
        if self.status.code == const.RECEIVING_COMPLETE_STATUS_KEY:
            inv_trans = self.save_inv_trans(inv_trans=self.inventory_transaction)
        elif self.status.code == const.RECEIVING_DRAFT_STATUS_KEY:
            for line in self.lines:
                line.price = line.purchase_order_line.unit_price
                line.product_id = line.purchase_order_line.product_id
                line.product = line.purchase_order_line.product
            inv_trans = self.save_inv_trans(inv_trans=self.inventory_transaction)

        if inv_trans is not None:
            self.inventory_transaction = inv_trans
            db.session.add(inv_trans)
        return inv_trans

    def save_inv_trans(self, inv_trans):
        from psi.app.models import EnumValues, InventoryTransaction, InventoryTransactionLine

        inv_type = EnumValues.get(const.PURCHASE_IN_INV_TRANS_KEY)
        if inv_trans is None:
            inv_trans = InventoryTransaction()
            inv_trans.type = inv_type
        inv_trans.date = self.date
        for line in self.lines:
            inv_line = line.inventory_transaction_line
            if inv_line is None:
                inv_line = InventoryTransactionLine()
                inv_line.product = line.product
                inv_line.inventory_transaction = inv_trans
                inv_line.inventory_transaction_id = inv_trans.id
                line.inventory_transaction_line = inv_line
            inv_line.price = line.price
            if self.status.code == const.RECEIVING_COMPLETE_STATUS_KEY:
                inv_line.quantity = line.quantity
                inv_line.in_transit_quantity = 0
                inv_line.saleable_quantity = line.quantity
            elif self.status.code == const.RECEIVING_DRAFT_STATUS_KEY:
                inv_line.quantity = 0
                inv_line.saleable_quantity = 0
                inv_line.in_transit_quantity = line.quantity
            line.inventory_transaction_line = inv_line
        for line in inv_trans.lines:
            if line.itl_receiving_line is None:
                db.session.delete(line)
        return inv_trans

    def can_delete(self):
        return self.receiving_in_draft()

    def can_edit(self, user=current_user):
        return self.receiving_in_draft()

    def receiving_in_draft(self):
        from psi.app.models import EnumValues
        draft_status = EnumValues.get(const.RECEIVING_DRAFT_STATUS_KEY)
        return self.status_id == draft_status.id


class ReceivingLine(db.Model):
    __tablename = 'receiving_line'
    id = Column(Integer, primary_key=True)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)

    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product', backref=backref('receiving_lines'))

    receiving_id = Column(Integer, ForeignKey('receiving.id'), nullable=False)
    receiving = relationship('Receiving', backref=backref('lines', uselist=True, cascade='all, delete-orphan'))

    purchase_order_line_id = Column(Integer, ForeignKey('purchase_order_line.id'), nullable=False)
    purchase_order_line = relationship('PurchaseOrderLine', backref=backref('pol_receiving_lines', uselist=True))

    inventory_transaction_line_id = Column(Integer, ForeignKey('inventory_transaction_line.id'), nullable=True)
    inventory_transaction_line = relationship('InventoryTransactionLine', backref=backref('itl_receiving_line', uselist=False, cascade='all, delete-orphan'))

    def __repr__(self):
        return "{0:s}{1:.0f}个(价格{2:.2f}元)".format(self.product.name, self.quantity, self.price)

    def __unicode__(self):
        return self.__repr__()

    @hybrid_property
    def total_amount(self):
        if self.quantity is None:
            q = 0
        else:
            q = self.quantity
        return format_decimal(Decimal(self.price * q))

    @total_amount.expression
    def total_amount(self):
        return select([self.price * self.quantity]).label('line_total_amount')

    @total_amount.setter
    def total_amount(self, value):
        pass

    @hybrid_property
    def transient_product(self):
        return self.product

    @transient_product.setter
    def transient_product(self, val):
        pass

    @hybrid_property
    def transient_price(self):
        return self.price

    @transient_price.setter
    def transient_price(self, val):
        pass
