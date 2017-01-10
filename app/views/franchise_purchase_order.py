# encoding=utf-8
from functools import partial

from flask.ext.login import current_user
from flask_babelex import lazy_gettext, gettext

from app import const
from app.models import Product, EnumValues
from app.utils import form_util, security_util, db_util
from app.views.base import DeleteValidator
from app.views.components import DisabledStringField
from app.views.base_purchase_order import BasePurchaseOrderAdmin
from app.views import SalesOrderAdmin


class FranchisePurchaseOrderAdmin(BasePurchaseOrderAdmin, DeleteValidator):

    type_code = const.FRANCHISE_PO_TYPE_KEY

    @property
    def role_identify(self):
        return "franchise_purchase_order"

    column_list = ('id', 'order_date', 'logistic_amount',
                   'goods_amount', 'total_amount', 'status', 'all_expenses',
                   'all_receivings', 'remark')

    form_columns = ('status', 'logistic_amount', 'order_date','goods_amount',
                    'total_amount', 'remark', 'lines')

    form_edit_rules = ('status', 'logistic_amount','order_date','goods_amount',
                       'total_amount', 'remark', 'lines')

    form_create_rules = ('status', 'order_date', 'logistic_amount',
                         'remark', 'lines')

    form_extra_fields = {
        "goods_amount": DisabledStringField(label=lazy_gettext('Goods Amount')),
        "total_amount": DisabledStringField(label=lazy_gettext('Total Amount')),
    }

    column_sortable_list = ('id', 'logistic_amount', 'total_amount',
                            ('status', 'status.display'),
                            'goods_amount', 'order_date',)

    column_details_list = ('id' , 'status', 'logistic_amount',
                           'order_date', 'goods_amount','total_amount','remark',
                           'lines', 'all_expenses', 'all_receivings')

    column_searchable_list = ('status.display', 'remark')

    def edit_form(self, obj=None):
        form = super(FranchisePurchaseOrderAdmin, self).edit_form(obj)
        # Set query_factory for newly added line
        parent_org_id = obj.to_organization.id
        form.lines.form.product.kwargs['query_factory'] = partial(
            Product.organization_filter, parent_org_id)
        if not security_util.user_has_role('purchase_price_view'):
            form_util.del_form_field(self, form, 'goods_amount')
            form_util.del_form_field(self, form, 'total_amount')
            form_util.del_inline_form_field(form.lines.form, form.lines.entries, 'total_amount')
        form_util.del_inline_form_field(form.lines.form, form.lines.entries, 'unit_price')
        # Set option list of status available
        if obj.status.code in [const.PO_RECEIVED_STATUS_KEY,
                               const.PO_PART_RECEIVED_STATUS_KEY,
                               const.PO_PART_RECEIVED_STATUS_KEY,
                               const.PO_ISSUED_STATUS_KEY,
                               const.PO_DRAFT_STATUS_KEY]:
            form.status.query = [EnumValues.find_one_by_code(obj.status.code), ]
        if obj.status.code == const.PO_DRAFT_STATUS_KEY:
            form.status.query.append(
                EnumValues.find_one_by_code(const.PO_ISSUED_STATUS_KEY))
        # Set product query option for old lines(forbid to change product for
        #  existing line)
        line_entries = form.lines.entries
        products = Product.organization_filter(parent_org_id).all()
        for sub_line in line_entries:
            sub_line.form.product.query = products
        return form

    def create_form(self, obj=None):
        form = super(FranchisePurchaseOrderAdmin, self).create_form(obj)
        form.status.query = [EnumValues.find_one_by_code(const.PO_DRAFT_STATUS_KEY), ]
        return form

    def on_model_change(self, form, model, is_created):
        from wtforms import ValidationError
        super(FranchisePurchaseOrderAdmin, self).on_model_change(form, model, is_created)
        for l in model.lines:
            if l.unit_price is None:
                l.unit_price = l.product.franchise_price
        if current_user.organization.type.code != const.FRANCHISE_STORE_ORG_TYPE_KEY:
            raise ValidationError(gettext("Your organization is not a franchise store and is not allowed to create franchise purchase order"))
        if current_user.organization.parent is None:
            raise ValidationError(gettext("Franchise purchase order creation failed, your organization does not have a valid parent organization"))
        if is_created:
                model.to_organization = current_user.organization.parent
        status = model.status
        if status.code == const.PO_ISSUED_STATUS_KEY:
            sales_order, incoming, expense = self.create_so_from_fpo(model)
            related_value = self.create_related_value(sales_order, model)
            db_util.save_objects_commit(sales_order, incoming, expense, related_value)

    @staticmethod
    def create_so_from_fpo(purchase_order):
        from app.models import SalesOrder, SalesOrderLine, EnumValues
        so_type = EnumValues.find_one_by_code(const.FRANCHISE_SO_TYPE_KEY)
        sales_order = SalesOrder()
        sales_order.id = db_util.get_next_id(SalesOrder)
        sales_order.order_date = purchase_order.order_date
        sales_order.type = so_type
        sales_order.remark = "PO ID: [{0}]".format(purchase_order.id)
        sales_order.organization = purchase_order.to_organization
        sales_order.status = EnumValues.find_one_by_code(const.SO_CREATED_STATUS_KEY)
        lines = []
        for line in purchase_order.lines:
            sol = SalesOrderLine()
            sol.unit_price = line.unit_price
            sol.quantity = line.quantity
            sol.sales_order = sales_order
            sol.product = line.product
            sol.remark = "PO Line ID:[{0}]".format(line.id)
            lines.append(sol)
        from app.services import SalesOrderService
        incoming = SalesOrderService.create_or_update_incoming(sales_order)
        expense = SalesOrderService.create_or_update_expense(sales_order)
        return sales_order, incoming, expense

    @staticmethod
    def create_related_value(sales_order, purchase_order):
        from app.models import RelatedValues
        rv = RelatedValues()
        rv.from_object_id = purchase_order.id
        rv.from_object_type = "PurchaseOrder"
        rv.to_object_id = sales_order.id
        rv.to_object_type = "SalesOrder"
        from app.const import FRANCHISE_PO_TO_SO_RT_KEY
        related_type = EnumValues.find_one_by_code(FRANCHISE_PO_TO_SO_RT_KEY)
        rv.relation_type = related_type
        return rv


