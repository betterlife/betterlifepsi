# encoding=utf-8
from functools import partial

from psi.app import const
from psi.app.models import Product, EnumValues
from psi.app.utils import form_util, security_util
from psi.app.views.base_purchase_order import BasePurchaseOrderAdmin
from psi.app.views.components import DisabledStringField
from flask_babelex import lazy_gettext

from psi.app.views.base import DeleteValidator


class DirectPurchaseOrderAdmin(BasePurchaseOrderAdmin, DeleteValidator):

    type_code = const.DIRECT_PO_TYPE_KEY

    @property
    def role_identify(self):
        return "direct_purchase_order"

    column_list = ('id', 'order_date', 'supplier','logistic_amount',
                   'goods_amount', 'total_amount', 'status', 'all_expenses',
                   'all_receivings', 'remark')

    form_columns = ('supplier', 'transient_supplier', 'status',
                    'logistic_amount', 'order_date','goods_amount',
                    'total_amount', 'remark', 'lines')

    form_edit_rules = ('transient_supplier', 'status', 'logistic_amount',
                       'order_date','goods_amount', 'total_amount',
                       'remark', 'lines')

    form_create_rules = ('supplier', 'status', 'order_date',
                         'logistic_amount', 'remark',)


    form_extra_fields = {
        "goods_amount": DisabledStringField(label=lazy_gettext('Goods Amount')),
        "total_amount": DisabledStringField(label=lazy_gettext('Total Amount')),
        'transient_supplier': DisabledStringField(label=lazy_gettext('Supplier'))
    }

    column_sortable_list = ('id', 'logistic_amount', 'total_amount',
                            ('status', 'status.display'),
                            'goods_amount', 'order_date',
                            ('supplier', 'supplier.id'),)

    column_details_list = ('id', 'supplier', 'status', 'logistic_amount',
                           'order_date', 'goods_amount','total_amount',
                           'remark', 'lines', 'all_expenses', 'all_receivings')

    column_searchable_list = ('supplier.name', 'status.display', 'remark')

    @property
    def column_filters(self):
        sl = list(super(DirectPurchaseOrderAdmin, self).column_filters)
        sl.append('supplier.name')
        return tuple(sl)

    def edit_form(self, obj=None):
        form = super(DirectPurchaseOrderAdmin, self).edit_form(obj)
        supplier_id = obj.transient_supplier.id
        # Set query_factory for newly added line
        form.lines.form.product.kwargs['query_factory'] = partial(
            Product.supplier_filter, supplier_id)
        if not security_util.user_has_role('purchase_price_view'):
            form_util.del_form_field(self, form, 'goods_amount')
            form_util.del_form_field(self, form, 'total_amount')
            form_util.del_inline_form_field(form.lines.form, form.lines.entries,
                                            'unit_price')
            form_util.del_inline_form_field(form.lines.form, form.lines.entries,
                                            'total_amount')
        # Set option list of status available
        if obj.status.code in [const.PO_RECEIVED_STATUS_KEY,
                               const.PO_PART_RECEIVED_STATUS_KEY,
                               const.PO_PART_RECEIVED_STATUS_KEY,
                               const.PO_ISSUED_STATUS_KEY,
                               const.PO_DRAFT_STATUS_KEY]:
            form.status.query = [EnumValues.get(obj.status.code), ]
        if obj.status.code == const.PO_DRAFT_STATUS_KEY:
            form.status.query.append(
                EnumValues.get(const.PO_ISSUED_STATUS_KEY))
        # Set product query option for old lines(forbid to change product for
        #  existing line)
        line_entries = form.lines.entries
        products = Product.supplier_filter(supplier_id).all()
        for sub_line in line_entries:
            sub_line.form.product.query = products
        return form

    def create_form(self, obj=None):
        from psi.app.models import Supplier
        form = super(DirectPurchaseOrderAdmin, self).create_form(obj)
        form.status.query = [EnumValues.get(const.PO_DRAFT_STATUS_KEY), ]
        form_util.filter_by_organization(form.supplier, Supplier)
        return form

