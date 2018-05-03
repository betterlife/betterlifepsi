from datetime import datetime

from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.model.fields import AjaxSelectField

from psi.app.models import Product
from psi.app import service
from psi.app.models import InventoryTransactionLine, InventoryTransaction
from psi.app.utils import security_util
from flask_admin.contrib.sqla.filters import FloatGreaterFilter, FloatSmallerFilter
from flask_admin.model import InlineFormAdmin
from flask_babelex import lazy_gettext

from .formatter import receivings_formatter, shipping_formatter, \
    default_date_formatter, type_field, date_field, product_field, price_field, \
    quantity_field, total_amount_field, remark_field, saleable_quantity_field, \
    line_formatter
from psi.app.views.base import ModelViewWithAccess, ModelWithLineFormatter


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
        from psi.app.views.components import DisabledStringField
        form.total_amount = DisabledStringField(label=lazy_gettext('Total Amount'))
        form.saleable_quantity = DisabledStringField(label=lazy_gettext('Saleable Quantity')),
        ajaxLoader = QueryAjaxModelLoader(name='product',
                                          session=service.Info.get_db().session,
                                          model=Product,
                                          fields=['name'])
        form.product = AjaxSelectField(ajaxLoader, label=lazy_gettext('Product(Can be searched by first letter)'))
        form.itl_receiving_line = None
        form.remark = None
        form.itl_shipping_line = None
        form.in_transit_quantity = None
        return form


class InventoryTransactionAdmin(ModelViewWithAccess, ModelWithLineFormatter):
    can_delete = False

    column_list = ('id', 'type', 'date', 'total_amount', 'it_receiving', 'it_shipping', 'remark')
    column_sortable_list = ('id', ('type', 'type.display'), 'total_amount', 'date',)
    form_columns = ('type', 'date', 'total_amount', 'remark', 'lines')
    form_create_rules = ('type', 'date', 'remark', 'lines',)
    form_edit_rules = ('type', 'date', 'remark', 'lines',)

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
        type=dict(query_factory=InventoryTransaction.manual_type_filter),
        date=dict(default=datetime.now()),
    )

    from psi.app.views.components import DisabledStringField

    form_extra_fields = {
        'total_amount': DisabledStringField(label=lazy_gettext('Total Amount')),
    }

    form_ajax_refs = {
        'product': QueryAjaxModelLoader(name='product',
                                        session=service.Info.get_db().session,
                                        model=Product,
                                        # --> Still need to filter the products by organization.
                                        # --> Line 209 is commented out, need to bring it back.
                                        fields=['name', 'mnemonic'])
    }

    column_formatters = {
        'it_receiving': receivings_formatter,
        'it_shipping': shipping_formatter,
        'date': default_date_formatter,
        'lines': line_formatter,
    }

    inline_models = (InventoryTransactionLineInlineAdmin(InventoryTransactionLine),)

    def get_list_columns(self):
        """
        This method is called instantly in list.html
        List of columns is decided runtime during render of the table
        Not decided during flask-admin blueprint startup.
        """
        columns = super(InventoryTransactionAdmin, self).get_list_columns()
        cols = ['total_amount']
        columns = security_util.filter_columns_by_role(
            columns, cols, 'purchase_price_view'
        )
        return columns

    def get_details_columns(self):
        cols = ['total_amount']
        columns = super(InventoryTransactionAdmin, self).get_details_columns()
        columns = security_util.filter_columns_by_role(
            columns, cols, 'purchase_price_view'
        )
        return columns

    @property
    def line_fields(self):
        if not security_util.user_has_role('purchase_price_view'):
            return [type_field, date_field, product_field, quantity_field,
                    saleable_quantity_field, remark_field]
        return [type_field, date_field, product_field, price_field,
                quantity_field, total_amount_field, saleable_quantity_field,
                remark_field]

