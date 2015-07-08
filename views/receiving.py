# coding=utf-8
from functools import partial
from flask.ext.admin.contrib.sqla import validators, ModelView
from flask.ext.admin.form import rules
from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext, gettext
from models import ReceivingLine, Receiving, PurchaseOrderLine, PurchaseOrder
from views import ModelViewWithAccess, DisabledStringField
from wtforms import BooleanField
from wtforms.validators import ValidationError


class ReceivingLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        purchase_order_line=dict(label=lazy_gettext('Purchase Order Line')),
        quantity=dict(label=lazy_gettext('Quantity')),
        price=dict(label=lazy_gettext('Receiving Price')),
    )

    def postprocess_form(self, form):
        form.remark = None
        form.inventory_transaction_line = None
        form.product = DisabledStringField(label=lazy_gettext('Product'))
        return form

class ReceivingAdmin(ModelViewWithAccess):
    inline_models = (ReceivingLineInlineAdmin(ReceivingLine),)
    column_list = ('id', 'purchase_order', 'status', 'date', 'remark')
    form_excluded_columns = ('inventory_transaction',)
    form_columns = ('purchase_order', 'transient_po', 'status', 'date', 'remark', 'lines', 'create_lines')
    form_edit_rules = ('transient_po', 'status', 'date', 'remark', 'lines')
    form_create_rules = (
        'purchase_order', 'status', 'date', 'remark', 'create_lines',
        rules.HTML('<div class="form-group">'
                   '<label for="remark" class="col-md-2 control-label">帮助</label>'
                   '<div class="col-md-10">'
                   '<input class="form-control" disabled="disabled" value="请先选择关联采购单后点击保存按钮，然后再增加收货明细行">'
                   '</div></div>')
    )
    form_extra_fields = {
        'create_lines': BooleanField(label=lazy_gettext('Create Lines for unreceived products'), ),
        'transient_po': DisabledStringField(label=lazy_gettext('Relate Purchase Order'))
    }
    form_widget_args = {
        'create_lines': {'default': True},
    }
    column_sortable_list = ('id', ('purchase_order', 'id'), ('status', 'status.display'), 'date',)
    column_labels = {
        'id': lazy_gettext('id'),
        'purchase_order': lazy_gettext('Relate Purchase Order'),
        'status': lazy_gettext('Status'),
        'date': lazy_gettext('Date'),
        'remark': lazy_gettext('Remark'),
        'lines': lazy_gettext('Lines'),
    }
    form_args = dict(
        status=dict(query_factory=Receiving.status_filter),
        purchase_order=dict(query_factory=partial(PurchaseOrder.status_filter,
                                                  ('PURCHASE_ORDER_ISSUED', 'PURCHASE_ORDER_PART_RECEIVED',))))
    def on_model_change(self, form, model, is_created):
        if is_created:
            # 1. Find all existing receiving bind with this PO.
            existing_res = Receiving.filter_by_po_id(model.purchase_order.id)
            available_info = {}
            if existing_res is not None:
                # 2. Calculate all received line and corresponding qty.
                received_qtys = self.get_received_quantities(existing_res)
                # 3. Calculate all not received line and corresponding qty
                for line in model.purchase_order.lines:
                    quantity = line.quantity
                    if line.id in received_qtys.keys():
                        quantity -= received_qtys[line.id]
                    available_info[line.id] = { 'quantity': quantity,'price': line.unit_price }
            else:
                # 3. Calculate all not received line and corresponding qty
                for line in model.purchase_order.lines:
                    available_info[line.id] = (line.quantity, line.unit_price)
             # 4. Create receiving lines based on the calculated result.
            if self.all_lines_received(available_info):
                raise ValidationError(gettext('There\'s no unreceived items in this PO.'))
            if model.create_lines:
                model.lines = self.create_receiving_lines(available_info)

    @staticmethod
    def all_lines_received(available_info):
        for line_id, line_info in available_info.iteritems():
            if line_info['quantity'] > 0:
                return False
        return True

    @staticmethod
    def create_receiving_lines(available_info):
        lines = []
        for line_id, line_info in available_info.iteritems():
            if line_info['quantity'] > 0:
                r_line = ReceivingLine()
                r_line.purchase_order_line_id = line_id
                r_line.quantity, r_line.price = line_info['quantity'], line_info['price']
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

    def edit_form(self, obj=None):
        form = super(ModelView, self).edit_form(obj)
        po_id = obj.transient_po.id
        line_entries = form.lines.entries
        po_lines = PurchaseOrderLine.header_filter(po_id).all()
        for sub_line in line_entries:
            sub_line.form.purchase_order_line.query = po_lines
        return form

    def on_form_prefill(self, form, id):
        pass

