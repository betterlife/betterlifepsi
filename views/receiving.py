# coding=utf-8
from functools import partial
from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext
from models import ReceivingLine, Receiving, PurchaseOrderLine, PurchaseOrder
from views import ModelViewWithAccess

class ReceivingLineInlineAdmin(InlineFormAdmin):
    def postprocess_form(self, form):
        form.remark = None
        form.inventory_transaction_line = None
        form.product = None
        return form

class ReceivingAdmin(ModelViewWithAccess):
    inline_models = (ReceivingLineInlineAdmin(ReceivingLine),)

    form_excluded_columns = ('inventory_transaction',)

    column_list = ('id', 'purchase_order', 'status', 'date', 'remark')

    column_labels = {
        'id': lazy_gettext('id'),
        'purchase_order': lazy_gettext('PurchaseOrder'),
        'status': lazy_gettext('Status'),
        'date': lazy_gettext('Date'),
        'remark': lazy_gettext('Remark'),
        'lines': lazy_gettext('Lines'),
    }

    form_args = dict(
        status=dict(query_factory=Receiving.status_filter),
        purchase_order=dict(query_factory=partial(PurchaseOrder.status_filter,
                                                  ('PURCHASE_ORDER_ISSUED', 'PURCHASE_ORDER_PART_RECEIVED',))))

    def on_form_prefill(self, form, id):
        if form is not None and form._obj is not None and form._obj.purchase_order_id is not None:
            po_id = form._obj.purchase_order_id
            form.lines.form.purchase_order_line.kwargs['query_factory'] =\
                partial(PurchaseOrderLine.header_filter, po_id)
