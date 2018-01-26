# coding=utf-8
from datetime import datetime
from functools import partial

from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader

from psi.app.views.formatter import product_field, quantity_field, \
    retail_price_field, \
    original_amount_field, remark_field, discount_amount_field, \
    actual_amount_field
from psi.app import service, const
from psi.app.models import EnumValues, Customer, Product
from psi.app.services.sales_order import SalesOrderService
from psi.app.utils import current_user, form_util
from psi.app.views.components import ReadonlyStringField, DisabledStringField
from flask_admin.model.template import BaseListRowAction
from flask_admin.contrib.sqla.filters import FloatGreaterFilter, FloatSmallerFilter, FloatEqualFilter
from flask_admin.model import InlineFormAdmin
from flask_babelex import lazy_gettext
from markupsafe import Markup

from psi.app.views.base import ModelViewWithAccess, ModelWithLineFormatter


class MarkInvalidRowAction(BaseListRowAction):
    def __init__(self, icon_class, title=None, id_arg='id', url_args=None):
        super(MarkInvalidRowAction, self).__init__(title=title)

        self.icon_class = icon_class
        self.id_arg = id_arg
        self.url_args = url_args

    def render(self, context, row_id, row):
        kwargs = dict(self.url_args) if self.url_args else {}
        kwargs[self.id_arg] = row_id
        so_invalid_status = EnumValues.get(const.SO_INVALID_STATUS_KEY)
        if row.status.code == const.SO_CREATED_STATUS_KEY and row.type.code == const.FRANCHISE_SO_TYPE_KEY:
            return Markup("""<a class='icon' href='javascript:MarkInvalidRowAction({0}, {1})'>
                               <span id='mark_invalid_row_action_{0}' class='fa fa-minus-circle'></span>
                            </a>""".format(row_id, so_invalid_status.id))
        else:
            return ''


class MarkShipRowAction(BaseListRowAction):
    def __init__(self, icon_class, title=None, id_arg='id', url_args=None):
        super(MarkShipRowAction, self).__init__(title=title)

        self.icon_class = icon_class
        self.id_arg = id_arg
        self.url_args = url_args

    def render(self, context, row_id, row):
        kwargs = dict(self.url_args) if self.url_args else {}
        kwargs[self.id_arg] = row_id
        so_shipped_status = EnumValues.get(const.SO_SHIPPED_STATUS_KEY)
        if row.status.code == const.SO_CREATED_STATUS_KEY and row.type.code == const.FRANCHISE_SO_TYPE_KEY:
            return Markup("""<a class='icon' href='javascript:MarkShipRowAction({0}, {1})'>
                               <span id='mark_ship_row_action_{0}' class='fa fa-truck'></span>
                            </a>""".format(row_id, so_shipped_status.id))
        else:
            return ''


class SalesOrderLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        unit_price=dict(label=lazy_gettext('Unit Price')),
        quantity=dict(label=lazy_gettext('Quantity')),
        remark=dict(label=lazy_gettext('Remark')),
    )

    def postprocess_form(self, form):
        from flask_admin.model.fields import AjaxSelectField
        ajaxLoader = QueryAjaxModelLoader(name='product',
                                          session=service.Info.get_db().session,
                                          model=Product,
                                          fields=['name'])
        form.product = AjaxSelectField(ajaxLoader, label=lazy_gettext('Product(Can be searched by first letter)'))
        form.retail_price = DisabledStringField(label=lazy_gettext('Retail Price'))
        form.price_discount = DisabledStringField(label=lazy_gettext('Price Discount'))
        form.original_amount = DisabledStringField(label=lazy_gettext('Original Amount'))
        form.actual_amount = DisabledStringField(label=lazy_gettext('Actual Amount'))
        form.discount_amount = DisabledStringField(label=lazy_gettext('Discount Amount'))
        form.remark = None
        form.sol_shipping_line = None
        form.external_id = None
        return form

    form_columns = ('id', 'product', 'unit_price', 'quantity',)


class SalesOrderAdmin(ModelViewWithAccess, ModelWithLineFormatter):
    from psi.app.models import SalesOrderLine, SalesOrder
    from .formatter import expenses_formatter, incoming_formatter, \
        shipping_formatter, default_date_formatter, line_formatter

    line_fields = [product_field, quantity_field, retail_price_field,
                   actual_amount_field, original_amount_field,
                   discount_amount_field, remark_field]

    column_extra_row_actions = [
        MarkShipRowAction('fa fa-camera-retro'),
        MarkInvalidRowAction('fa fa-minus-circle')
    ]

    column_list = ('id', 'type', 'status', 'customer', 'logistic_amount', 'actual_amount', 'original_amount',
                   'discount_amount', 'order_date', 'incoming', 'expense', 'so_shipping', 'remark')
    column_filters = ('order_date', 'logistic_amount',
                      FloatSmallerFilter(SalesOrder.actual_amount, lazy_gettext('Actual Amount')),
                      FloatGreaterFilter(SalesOrder.actual_amount, lazy_gettext('Actual Amount')),
                      FloatEqualFilter(SalesOrder.actual_amount, lazy_gettext('Actual Amount')),
                      FloatSmallerFilter(SalesOrder.discount_amount, lazy_gettext('Discount Amount')),
                      FloatGreaterFilter(SalesOrder.discount_amount, lazy_gettext('Discount Amount')),
                      FloatEqualFilter(SalesOrder.discount_amount, lazy_gettext('Discount Amount')),
                      FloatSmallerFilter(SalesOrder.original_amount, lazy_gettext('Total Amount')),
                      FloatGreaterFilter(SalesOrder.original_amount, lazy_gettext('Total Amount')),
                      FloatEqualFilter(SalesOrder.original_amount, lazy_gettext('Total Amount')),)

    column_searchable_list = ('customer.first_name', 'customer.last_name', 'remark', 'type.display', 'type.code',
                              'status.display', 'status.code', 'customer.mobile_phone', 'customer.email',
                              'customer.address', 'customer.level.display', 'customer.join_channel.display')

    form_columns = ('id', 'customer', 'logistic_amount', 'status', 'order_date', 'remark', 'actual_amount',
                    'original_amount', 'discount_amount', 'lines')
    form_edit_rules = ('customer', 'logistic_amount', 'order_date', 'status', 'remark', 'actual_amount',
                       'original_amount', 'discount_amount', 'lines')
    form_create_rules = ('customer', 'logistic_amount',  'order_date', 'status', 'remark', 'lines',)

    column_details_list = ('id', 'type', 'status', 'customer', 'external_id', 'logistic_amount', 'order_date', 'remark',
                           'actual_amount', 'original_amount', 'discount_amount', 'incoming', 'expense',
                           'so_shipping', 'lines',)

    column_editable_list = ('remark',)

    form_extra_fields = {
        'transient_external_id': DisabledStringField(label=lazy_gettext('External Id')),
        'actual_amount': DisabledStringField(label=lazy_gettext('Actual Amount')),
        'original_amount': DisabledStringField(label=lazy_gettext('Original Amount')),
        'discount_amount': DisabledStringField(label=lazy_gettext('Discount Amount'))
    }

    form_overrides = dict(external_id=ReadonlyStringField)

    form_args = dict(
        logistic_amount=dict(default=0),
        order_date=dict(default=datetime.now()),
        status=dict(query_factory=SalesOrder.status_option_filter),
        customer=dict(description=lazy_gettext('Customer can be searched by name, mobile phone, email or first letter of his/her name'))
    )

    form_excluded_columns = ('incoming', 'expense', 'so_shipping')
    column_sortable_list = ('id', 'logistic_amount', 'actual_amount', 'original_amount', 'discount_amount',
                            'order_date',('status', 'status.display'), ('type', 'type.display'))

    form_ajax_refs = {
        'customer': QueryAjaxModelLoader('customer',
                                         service.Info.get_db().session, Customer,
                                         filters=[],
                                         fields=['first_name', 'last_name', 'mobile_phone', 'email', 'mnemonic']),
        'product': QueryAjaxModelLoader(name='product',
                                        session=service.Info.get_db().session,
                                        model=Product,
                                        # --> Still need to filter the products by organization.
                                        # --> Line 209 is commented out, need to bring it back.
                                        fields=['name', 'mnemonic'])
    }

    inline_models = (SalesOrderLineInlineAdmin(SalesOrderLine),)

    column_formatters = {
        'expense': expenses_formatter,
        'incoming': incoming_formatter,
        'so_shipping': shipping_formatter,
        'order_date': default_date_formatter,
        'lines': line_formatter,
    }

    column_labels = {
        'id': lazy_gettext('id'),
        'logistic_amount': lazy_gettext('Logistic Amount'),
        'order_date': lazy_gettext('Order Date'),
        'remark': lazy_gettext('Remark'),
        'actual_amount': lazy_gettext('Actual Amount'),
        'original_amount': lazy_gettext('Original Amount'),
        'discount_amount': lazy_gettext('Discount Amount'),
        'incoming': lazy_gettext('Related Incoming'),
        'expense': lazy_gettext('Related Expense'),
        'so_shipping': lazy_gettext('Related Shipping'),
        'lines': lazy_gettext('Lines'),
        'external_id': lazy_gettext('External Id'),
        'customer': lazy_gettext('Customer'),
        'customer.name': lazy_gettext('Customer'),
        'status': lazy_gettext('Status'),
        'type': lazy_gettext('Type'),
    }

    def create_form(self, obj=None):
        form = super(SalesOrderAdmin, self).create_form(obj)
        self.hide_line_derive_fields_on_create_form(form)
        form_util.filter_by_organization(form.customer, Customer)
        self.filter_product_by_organization(form)
        return form

    def hide_line_derive_fields_on_create_form(self, form):
        form.lines.form.actual_amount = None
        form.lines.form.discount_amount = None
        form.lines.form.original_amount = None
        form.lines.form.price_discount = None
        form.lines.form.retail_price = None

    def edit_form(self, obj=None):
        form = super(SalesOrderAdmin, self).edit_form(obj)
        form_util.filter_by_organization(form.customer, Customer)
        self.filter_product_by_organization(form)
        return form

    @staticmethod
    def filter_product_by_organization(form):
        # Set query factory for new created line
        # TODO.xqliu Fix this for AJAX lookup
        # If we uncomment follow line to limit the query to current organization
        # The AJAX look up fails.
        # form.lines.form.product.kwargs['query_factory'] = partial(Product.organization_filter, current_user.organization_id)
        # Set query object filter for existing lines
        line_entries = form.lines.entries
        for sub_line in line_entries:
            form_util.filter_by_organization(sub_line.form.product, Product)

    def on_model_change(self, form, model, is_created):
        super(SalesOrderAdmin, self).on_model_change(form, model, is_created)
        if is_created:
            model.type = EnumValues.get(const.DIRECT_SO_TYPE_KEY)
            if model.status is None:
                model.status = EnumValues.get(const.SO_DELIVERED_STATUS_KEY)
            model.organization = current_user.organization
        if model.status.code == const.SO_DELIVERED_STATUS_KEY:
            incoming = SalesOrderService.create_or_update_incoming(model)
            expense = SalesOrderService.create_or_update_expense(model)
            shipping = None
            if model.type.code == const.DIRECT_SO_TYPE_KEY:
                shipping = SalesOrderService.create_or_update_shipping(model)
            db = service.Info.get_db()
            if expense is not None:
                db.session.add(expense)
            if incoming is not None:
                db.session.add(incoming)
            if shipping is not None:
                db.session.add(shipping)

    @property
    def role_identify(self):
        return "direct_sales_order"
