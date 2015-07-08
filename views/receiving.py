# coding=utf-8
from functools import partial
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext
from models import ReceivingLine, Receiving, PurchaseOrderLine, PurchaseOrder
from views import ModelViewWithAccess
from views.custom_fields import ReadonlyStringField


class ReceivingLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        purchase_order_line=dict(label=lazy_gettext('Purchase Order Line')),
        quantity=dict(label=lazy_gettext('Quantity')),
        price=dict(label=lazy_gettext('Receiving Price')),
    )

    def postprocess_form(self, form):
        form.remark = None
        form.inventory_transaction_line = None
        form.product = None
        return form

class ReceivingAdmin(ModelViewWithAccess):
    inline_models = (ReceivingLineInlineAdmin(ReceivingLine),)

    form_excluded_columns = ('inventory_transaction',)

    form_edit_rules = ('purchase_order', 'status', 'date', 'remark', 'lines')

    form_create_rules = ('purchase_order', 'status', 'date', 'remark')

    column_sortable_list = ('id', ('purchase_order', 'id'), ('status', 'status.display'), 'date',)

    column_list = ('id', 'purchase_order', 'status', 'date', 'remark')

    column_labels = {
        'id': lazy_gettext('id'),
        'purchase_order': lazy_gettext('PurchaseOrder'),
        'status': lazy_gettext('Status'),
        'date': lazy_gettext('Date'),
        'remark': lazy_gettext('Remark'),
        'lines': lazy_gettext('Lines'),
    }

    form_columns = ('purchase_order', 'status', 'date', 'remark', 'lines',)

    form_args = dict(
        status=dict(query_factory=Receiving.status_filter),
        purchase_order=dict(query_factory=partial(PurchaseOrder.status_filter,
                                                  ('PURCHASE_ORDER_ISSUED', 'PURCHASE_ORDER_PART_RECEIVED',))))

    def on_form_prefill(self, form, id):
        if form is not None \
                and form._obj is not None \
                and form._obj.purchase_order_id is not None\
                and form.lines is not None\
                and form.lines.form is not None:
            po_id = form._obj.purchase_order_id
            form.lines.form.purchase_order_line.kwargs['query_factory'] =\
                partial(PurchaseOrderLine.header_filter, po_id)
