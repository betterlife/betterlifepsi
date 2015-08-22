# coding=utf-8
from datetime import datetime
from functools import partial

from app.app_provider import AppInfo
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.model import InlineFormAdmin
from app import const
from flask.ext.babelex import lazy_gettext, gettext
from app.models import ReceivingLine, Receiving, PurchaseOrderLine, PurchaseOrder, InventoryTransaction, EnumValues, \
    InventoryTransactionLine
from app.views import ModelViewWithAccess, DisabledStringField
from formatter import supplier_formatter, purchase_order_formatter, inventory_transaction_formatter, \
    default_date_formatter
from app.views.base import DeleteValidator
from wtforms import BooleanField
from wtforms.validators import ValidationError


class ReceivingLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        purchase_order_line=dict(label=lazy_gettext('Purchase Order Line')),
        quantity=dict(label=lazy_gettext('Quantity')),
        total_amount=dict(label=lazy_gettext('Total Amount')),
    )

    def postprocess_form(self, form):
        form.remark = None
        form.inventory_transaction_line = None
        form.product = None
        form.transient_price = DisabledStringField(label=lazy_gettext('Receiving Price'),
                                                   description=lazy_gettext('Receiving price is brought from purchase '
                                                                            'order and can not be modified in '
                                                                            'receiving line'))
        form.total_amount = DisabledStringField(label=lazy_gettext('Total Amount'))
        form.transient_product = DisabledStringField(label=lazy_gettext('Product'))
        form.price = None
        return form


class ReceivingAdmin(ModelViewWithAccess, DeleteValidator):
    inline_models = (ReceivingLineInlineAdmin(ReceivingLine),)
    column_list = ('id', 'purchase_order', 'supplier', 'date', 'status', 'total_amount', 'inventory_transaction',
                   'remark')
    form_excluded_columns = ('inventory_transaction',)
    form_columns = ('purchase_order', 'transient_po', 'status', 'date',
                    'total_amount', 'remark', 'lines', 'create_lines')
    form_edit_rules = ('transient_po', 'status', 'date', 'total_amount', 'remark', 'lines',)
    column_editable_list = ('remark',)
    form_create_rules = ('purchase_order', 'status', 'date', 'remark', 'create_lines',)
    form_extra_fields = {
        'create_lines': BooleanField(label=lazy_gettext('Create Lines for unreceived products'),
                                     description=lazy_gettext('Create receiving lines based on '
                                                              'not yet received products in the purchase order')),
        'transient_po': DisabledStringField(label=lazy_gettext('Related Purchase Order')),
        "total_amount": DisabledStringField(label=lazy_gettext('Total Amount')),
    }
    form_widget_args = {
        'create_lines': {'default': True},
    }
    column_sortable_list = ('id', ('supplier', 'id'), ('purchase_order', 'id'), ('status', 'status.display'), 'date',
                            'total_amount')
    column_labels = {
        'id': lazy_gettext('id'),
        'purchase_order': lazy_gettext('Related Purchase Order'),
        'supplier': lazy_gettext('Supplier'),
        'status': lazy_gettext('Status'),
        'date': lazy_gettext('Date'),
        'remark': lazy_gettext('Remark'),
        'total_amount': lazy_gettext('Total Amount'),
        'inventory_transaction': lazy_gettext('Inventory Transaction'),
        'lines': lazy_gettext('Lines'),
    }
    form_args = dict(
        status=dict(query_factory=Receiving.status_filter,
                    description=lazy_gettext('Current status of the receiving document, '
                                             'completed receiving can not be updated or deleted')),
        purchase_order=dict(description=lazy_gettext(
            'Please select a purchase order and save the form, then add receiving lines accordingly'),
            query_factory=partial(PurchaseOrder.status_filter,
                                  (const.PO_ISSUED_STATUS_KEY, const.PO_PART_RECEIVED_STATUS_KEY,))),
        date=dict(default=datetime.now()),
    )

    column_formatters = {
        'supplier': supplier_formatter,
        'purchase_order': purchase_order_formatter,
        'inventory_transaction': inventory_transaction_formatter,
        'date': default_date_formatter,
    }

    def on_model_delete(self, model):
        DeleteValidator.validate_status_for_change(model, const.RECEIVING_COMPLETE_STATUS_KEY,
                                                   gettext('Receiving document can not be update '
                                                           'nor delete on complete status'))

    def on_model_change(self, form, model, is_created):
        if is_created:
            available_info = self.get_available_lines_info(model)
            # 4. Check any qty available for receiving?
            if self.all_lines_received(available_info):
                raise ValidationError(gettext('There\'s no unreceived items in this PO.'))
            # 5. Create receiving lines based on the calculated result.
            if model.create_lines:
                model.lines = self.create_receiving_lines(available_info)
        self.operate_inv_trans_by_recv_status(model)
        self.update_purchase_order_status(model)
        AppInfo.get_db().session.commit()

    def update_purchase_order_status(self, model):
        if model.status.code == const.RECEIVING_COMPLETE_STATUS_KEY:
            po = model.purchase_order
            finished = False
            started = False
            for line in po.lines:
                receiving_lines = line.pol_receiving_lines
                rd_qty = 0
                for rl in receiving_lines:
                    rd_qty += rl.quantity
                if rd_qty > 0:
                    started = True
                if rd_qty >= line.quantity:
                    finished = True
            if finished is True:
                po.status = EnumValues.find_one_by_code(const.PO_RECEIVED_STATUS_KEY)
            elif started is True:
                po.status = EnumValues.find_one_by_code(const.PO_PART_RECEIVED_STATUS_KEY)
            AppInfo.get_db().session.add(po)


    def operate_inv_trans_by_recv_status(self, model):
        inv_trans = None
        if model.status.code == const.RECEIVING_COMPLETE_STATUS_KEY:
            inv_trans = self.save_inv_trans(model, inv_trans=model.inventory_transaction,
                                            set_qty_func=ReceivingAdmin.set_qty_completed)
        elif model.status.code == const.RECEIVING_DRAFT_STATUS_KEY:
            for line in model.lines:
                line.price = line.purchase_order_line.unit_price
                line.product_id = line.purchase_order_line.product_id
            inv_trans = self.save_inv_trans(model, inv_trans=model.inventory_transaction,
                                            set_qty_func=ReceivingAdmin.set_qty_draft)

        if inv_trans is not None:
            model.inventory_transaction = inv_trans
            AppInfo.get_db().session.add(inv_trans)

    @staticmethod
    def save_inv_trans(model, inv_trans, set_qty_func):
        inv_type = EnumValues.find_one_by_code(const.PURCHASE_IN_INV_TRANS_KEY)
        if inv_trans is None:
            inv_trans = InventoryTransaction()
            inv_trans.type_id = inv_type.id
        inv_trans.date = model.date
        for line in model.lines:
            inv_line = line.inventory_transaction_line
            if inv_line is None:
                inv_line = InventoryTransactionLine()
                inv_line.product = line.product
                inv_line.inventory_transaction = inv_trans
                inv_line.inventory_transaction_id = inv_trans.id
                line.inventory_transaction_line = inv_line
            inv_line.price = line.price
            set_qty_func(inv_line, line)
        return inv_trans

    @staticmethod
    def set_qty_completed(inv_line, recv_line):
        inv_line.quantity = recv_line.quantity
        inv_line.in_transit_quantity = 0

    @staticmethod
    def set_qty_draft(inv_line, recv_line):
        inv_line.quantity = 0
        inv_line.in_transit_quantity = recv_line.quantity

    def get_available_lines_info(self, model):
        # 1. Find all existing receiving bind with this PO.
        existing_res = Receiving.filter_by_po_id(model.purchase_order.id)
        available_info = {}
        if existing_res is not None:
            # 2. Calculate all received line and corresponding qty.
            received_qtys = self.get_received_quantities(existing_res)
            # 3. Calculate all un-received line and corresponding qty
            for line in model.purchase_order.lines:
                quantity = line.quantity
                if line.id in received_qtys.keys():
                    quantity -= received_qtys[line.id]
                available_info[line.id] = {
                    'line': line, 'quantity': quantity,
                    'price': line.unit_price, 'product_id': line.product_id
                }
        else:
            # 3. Calculate un-received line info(qty, price) if there's no existing receiving
            for line in model.purchase_order.lines:
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
        lines = []
        for id, info in available_info.iteritems():
            if info['quantity'] > 0:
                r_line = ReceivingLine()
                r_line.purchase_order_line_id = id
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

    def create_form(self, obj=None):
        form = super(ModelView, self).create_form(obj)
        form.status.query = [EnumValues.find_one_by_code(const.RECEIVING_DRAFT_STATUS_KEY),]
        form.create_lines.data = True
        return form

    def edit_form(self, obj=None):
        form = super(ModelView, self).edit_form(obj)
        po_id = obj.transient_po.id
        # Set query_factory for newly added line
        form.lines.form.purchase_order_line.kwargs['query_factory'] =\
            partial(PurchaseOrderLine.header_filter, po_id)
        if obj is not None and obj.status is not None and obj.status.code == const.RECEIVING_COMPLETE_STATUS_KEY:
            form.status.query = [EnumValues.find_one_by_code(const.RECEIVING_COMPLETE_STATUS_KEY),]
        # Set query option for old lines
        line_entries = form.lines.entries
        po_lines = PurchaseOrderLine.header_filter(po_id).all()
        for sub_line in line_entries:
            sub_line.form.purchase_order_line.query = po_lines
        return form
