from datetime import datetime

from flask_admin.contrib.sqla.filters import FloatGreaterFilter, FloatSmallerFilter
from flask_admin.model import InlineFormAdmin
from flask_babelex import lazy_gettext
from app.models import InventoryTransactionLine, InventoryTransaction
from app.views.base import ModelViewWithAccess
from formatter import receivings_formatter, shipping_formatter, default_date_formatter


class InventoryTransactionLineInlineAdmin(InlineFormAdmin):

    form_args = dict(
        id=dict(label=lazy_gettext('id')),
        product=dict(label=lazy_gettext('Product')),
        price=dict(label=lazy_gettext('Inventory Transaction Price'),
                   description=lazy_gettext('For sales, it should be sell price, '
                                            'for item lost or broken, should be purchase price plus logistic expend')),
        in_transit_quantity=dict(label=lazy_gettext('In Transit Quantity'),
                                 description=lazy_gettext('Quantity of product ordered but still on the way')),
        quantity=dict(label=lazy_gettext('Actual Quantity Change'),
                      description=lazy_gettext('This quantity should be a negative number '
                                               'for sales, item lost or item broken')),
        remark=dict(label=lazy_gettext('Remark')),
    )

    def postprocess_form(self, form):
        from app.views.custom_fields import DisabledStringField
        form.total_amount = DisabledStringField(label=lazy_gettext('Total Amount'))
        form.itl_receiving_line = None
        form.remark = None
        form.itl_shipping_line = None
        return form


class InventoryTransactionAdmin(ModelViewWithAccess):
    can_delete = False

    column_list = ('id', 'type', 'date', 'total_amount', 'it_receiving', 'it_shipping', 'remark')
    column_sortable_list = ('id', ('type', 'type.display'), 'total_amount', 'date',)
    form_columns = ('type', 'date', 'total_amount', 'remark', 'lines')
    form_create_rules = ('type', 'date', 'remark', 'lines',)
    column_editable_list = ('remark',)

    column_filters = ('date',
                      FloatGreaterFilter(InventoryTransaction.total_amount, lazy_gettext('Total Amount')),
                      FloatSmallerFilter(InventoryTransaction.total_amount, lazy_gettext('Total Amount')),)
    column_searchable_list = ('type.display', 'remark')

    column_details_list = ('id', 'type', 'date', 'total_amount', 'remark', 'lines', 'it_receiving', 'it_shipping',)

    column_labels = {
        'id': lazy_gettext('id'),
        'type': lazy_gettext('Inventory Transaction Type'),
        'date': lazy_gettext('Date'),
        'total_amount': lazy_gettext('Total Amount'),
        'remark': lazy_gettext('Remark'),
        'lines': lazy_gettext('Lines'),
        'it_receiving': lazy_gettext('Related Receiving'),
        'it_shipping': lazy_gettext('Related Shipping'),
    }

    form_excluded_columns = ('it_shipping', 'it_receiving')

    form_args = dict(
        type=dict(query_factory=InventoryTransaction.type_filter),
        date=dict(default=datetime.now()),
    )

    from app.views.custom_fields import DisabledStringField

    form_extra_fields = {
        'total_amount': DisabledStringField(label=lazy_gettext('Total Amount')),
    }

    column_formatters = {
        'it_receiving': receivings_formatter,
        'it_shipping': shipping_formatter,
        'date': default_date_formatter,
    }

    inline_models = (InventoryTransactionLineInlineAdmin(InventoryTransactionLine),)
