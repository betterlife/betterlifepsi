# coding=utf-8
from datetime import datetime

from flask_admin.contrib.sqla.filters import FloatSmallerFilter, FloatGreaterFilter, FloatEqualFilter
from flask_admin.model import InlineFormAdmin
from flask_babelex import lazy_gettext, gettext
from wtforms import ValidationError

from psi.app.utils import security_util
from psi.app.views.base import ModelWithLineFormatter
from psi.app.views.components import DisabledStringField
from psi.app.views import ModelViewWithAccess
from psi.app.views.formatter import quantity_field, price_field, \
    total_amount_field, line_formatter, product_field


class ShippingLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        sales_order_line=dict(label=lazy_gettext('Related Sales Order Line')),
        quantity=dict(label=lazy_gettext('Quantity')),
        price=dict(label=lazy_gettext('Unit Price')),
        total_amount=dict(label=lazy_gettext('Total Amount')),
        product=dict(label=lazy_gettext('Product')),
    )

    def postprocess_form(self, form):
        form.remark = None
        form.inventory_transaction_line = None
        form.total_amount = DisabledStringField(label=lazy_gettext('Total Amount'))
        return form


class ShippingAdmin(ModelViewWithAccess, ModelWithLineFormatter):

    from .formatter import inventory_transaction_formatter, sales_order_formatter, default_date_formatter
    from psi.app.models import ShippingLine, Shipping

    inline_models = (ShippingLineInlineAdmin(ShippingLine),)
    column_list = ('id', 'status', 'date', 'total_amount', 'sales_order', 'inventory_transaction', 'remark')

    can_edit = False
    can_create = False
    can_delete = False

    form_columns = ('sales_order', 'status', 'date', 'total_amount', 'remark', 'lines')
    form_extra_fields = {
        "total_amount": DisabledStringField(label=lazy_gettext('Total Amount')),
    }

    column_filters = ('date',
                      FloatSmallerFilter(Shipping.total_amount, lazy_gettext('Total Amount')),
                      FloatGreaterFilter(Shipping.total_amount, lazy_gettext('Total Amount')),
                      FloatEqualFilter(Shipping.total_amount, lazy_gettext('Total Amount')),)
    column_searchable_list = ('status.display', 'remark')

    @property
    def column_details_list(self):
        if not security_util.user_has_role('purchase_price_view'):
            return ('id', 'sales_order', 'status', 'date', 'remark', 'lines', 'inventory_transaction')
        return ('id', 'sales_order', 'status', 'date', 'total_amount', 'remark', 'lines', 'inventory_transaction')

    @property
    def line_fields(self):
        # TODO.xqliu Move the judgetment stragegy to a separate method to avoid repeat myself!!!
        if not security_util.user_has_role('purchase_price_view'):
            return [product_field, quantity_field]
        return [product_field, price_field, quantity_field, price_field, total_amount_field]

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
        'status.display': lazy_gettext('Status'),
    }

    form_args = dict(
        status=dict(query_factory=Shipping.status_filter, ),
        date=dict(default=datetime.now()),
        lines=dict(description=lazy_gettext('Modify shipping document directly is not allowed, '
                                            'please modify the related sales order and this shipping document '
                                            'will be changed accordingly')),
    )

    column_formatters = {
        'inventory_transaction': inventory_transaction_formatter,
        'sales_order': sales_order_formatter,
        'date': default_date_formatter,
        'lines': line_formatter
    }

    def on_model_change(self, form, model, is_created):
        raise ValidationError(gettext('Modify shipping document directly is not allowed, '
                                      'please modify the related sales order and this shipping document '
                                      'will be changed accordingly'))
