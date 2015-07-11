# coding=utf-8
from datetime import datetime
from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext, gettext
from models import ShippingLine, Shipping
from views import ModelViewWithAccess, DisabledStringField
from views.base import DeleteValidator
from wtforms import ValidationError


class ShippingLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        sales_order_line=dict(label=lazy_gettext('Related Sales Order Line')),
        quantity=dict(label=lazy_gettext('Quantity')),
        price=dict(label=lazy_gettext('Unit Price')),
        total_amount=dict(label=lazy_gettext('Total Amount')),
    )

    def postprocess_form(self, form):
        form.remark = None
        form.inventory_transaction_line = None
        form.total_amount = DisabledStringField(label=lazy_gettext('Total Amount'))
        form.product = DisabledStringField(label=lazy_gettext('Product'))
        return form


class ShippingAdmin(ModelViewWithAccess):
    inline_models = (ShippingLineInlineAdmin(ShippingLine),)
    column_list = ('id', 'status', 'date', 'total_amount', 'sales_order', 'inventory_transaction', 'remark')

    can_edit = True
    can_create = False
    can_delete = False

    form_columns = ('sales_order', 'status', 'date', 'inventory_transaction', 'total_amount', 'remark', 'lines')
    form_extra_fields = {
        "total_amount": DisabledStringField(label=lazy_gettext('Total Amount')),
    }

    column_sortable_list = ('id', ('sales_order', 'id'), ('status', 'status.display'), 'date', 'total_amount')
    column_labels = {
        'id': lazy_gettext('id'),
        'sales_order': lazy_gettext('Related Sales Order'),
        'status': lazy_gettext('Status'),
        'date': lazy_gettext('Date'),
        'remark': lazy_gettext('Remark'),
        'total_amount': lazy_gettext('Total Amount'),
        'inventory_transaction': lazy_gettext('Inventory Transaction'),
        'lines': lazy_gettext('Lines'),
    }
    form_args = dict(
        status=dict(query_factory=Shipping.status_filter,),
        date=dict(default=datetime.now()),
        sales_order=dict(description=lazy_gettext('Modify shipping document directly is not allowed, '
                                                  'please modify the related sales order and this shipping document '
                                                  'will be changed accordingly'))
    )

    def on_model_change(self, form, model, is_created):
        raise ValidationError(gettext('Modify shipping document directly is not allowed, '
                                      'please modify the related sales order and this shipping document '
                                      'will be changed accordingly'))
