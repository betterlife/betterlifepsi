# coding=utf-8
from functools import partial
from flask.ext.admin.contrib.sqla import validators
from flask.ext.admin.form import rules
from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext
from models import ReceivingLine, Receiving, PurchaseOrderLine, PurchaseOrder
from views import ModelViewWithAccess, DisabledStringField
from wtforms import BooleanField
from wtforms.validators import optional


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
    column_list = ('id', 'transient_po', 'purchase_order', 'status', 'date', 'remark')
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
            if model.create_lines:
                pass
                #1. Find all existing receiving bind with this PO.
                #2. Calculate all received line and corresponding qty.
                #3. Calculate all not received line and corresponding qty
                #4. Create receiving lines based on the calculated result.

    def on_form_prefill(self, form, id):
        if form is not None \
                and form._obj is not None \
                and form._obj.purchase_order_id is not None\
                and form.lines is not None\
                and form.lines.form is not None:
            po_id = form._obj.purchase_order_id
            form.lines.form.purchase_order_line.kwargs['query_factory'] =\
                partial(PurchaseOrderLine.header_filter, po_id)
