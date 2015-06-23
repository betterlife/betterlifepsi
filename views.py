# coding=utf-8
from flask.ext.admin import Admin
from flask.ext.admin.consts import ICON_TYPE_GLYPH
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.model import InlineFormAdmin
from models import Product, Supplier, PurchaseOrder, SalesOrder, Expense, Incoming, EnumValues, ProductCategory
from wtforms import StringField, TextField


class ProductCategoryAdmin(ModelView):
    column_exclude_list = ['sub_categories', 'products']
    column_sortable_list = ('code', 'name')
    column_searchable_list = ('code', 'name')
    column_filters = ('code','name')
    column_editable_list = ['code', 'name']
    form_widget_args = {
        # 'sub_categories': { 'disabled': True },
        # 'products' : { 'disabled' : True },
    }
    form_args = dict(
        parent_category = dict(label='Parent',)
    )

class ProductAdmin(ModelView):
    column_editable_list = ['name', 'deliver_day', 'lead_day', 'distinguishing_feature', 'spec_link', 'purchase_price', 'retail_price']
    column_searchable_list = ('code', 'name', 'supplier.name', 'category.name', 'category.code')
    column_filters = column_searchable_list


class SupplierAdmin(ModelView):
    from models import PaymentMethod
    form_excluded_columns = ('purchaseOrders',)
    inline_models = (PaymentMethod,)
    column_editable_list = ['name', 'qq', 'phone', 'contact', 'email', 'website', 'whole_sale_req', 'can_mixed_whole_sale', 'remark']
    column_searchable_list = ('code', 'name')
    column_filters = column_searchable_list


class PaymentMethodAdmin(ModelView):
    column_editable_list = ['account_name', 'account_number', 'bank_name', 'bank_branch', 'remark']

class ReadOnlyStringField(StringField):
    def __call__(self, **kwargs):
        kwargs['disabled'] = True
        return super(ReadOnlyStringField, self).__call__(**kwargs)


class PurchaseOrderLineInlineAdmin(InlineFormAdmin):

    def postprocess_form(self, form):
        form.total_amount = ReadOnlyStringField(label='Total Amount')
        return form

    def on_model_change(self, form, model):
        print model, form

class PurchaseOrderAdmin(ModelView):
    from models import PurchaseOrderLine
    column_list = ('logistic_amount','other_amount', 'total_amount', 'order_date','supplier', 'remark')
    form_extra_fields = {
        "total_amount": StringField('Total Amount')
    }
    form_widget_args = {
        'total_amount': {'disabled': True},
    }
    inline_models = (PurchaseOrderLineInlineAdmin(PurchaseOrderLine),)

class SalesOrderAdmin(ModelView):
    from models import SalesOrderLine
    inline_models = (SalesOrderLine,)

class IncomingAdmin(ModelView):
    form_args = dict(
        status=dict(query_factory=Incoming.status_filter),
        category=dict(query_factory=Incoming.type_filter),
    )

class ExpenseAdmin(ModelView):
    form_args = dict(
        status=dict(query_factory=Expense.status_filter),
        category=dict(query_factory=Expense.type_filter),
    )

class EnumValuesAdmin(ModelView):
    column_editable_list = ['display']
    column_searchable_list = ['code', 'display']
    column_filters = ('code', 'display',)

def init_admin_views(app, db):
    db_session = db.session
    admin = Admin(app, u'管理后台', base_template='layout.html', template_mode='bootstrap3')
    admin.add_view(ProductAdmin(Product, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-barcode'))
    admin.add_view(SupplierAdmin(Supplier, db_session,  menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-globe'))
    admin.add_view(PurchaseOrderAdmin(PurchaseOrder, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-shopping-cart'))
    admin.add_view(SalesOrderAdmin(SalesOrder, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-send'))
    admin.add_view(ExpenseAdmin(Expense, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-usd'))
    admin.add_view(IncomingAdmin(Incoming, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-minus-sign'))
    admin.add_view(EnumValuesAdmin(EnumValues, db_session, category='Settings', name='基础分类', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tasks'))
    admin.add_view(ProductCategoryAdmin(ProductCategory, db_session, category='Settings', name='产品分类', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tags'))
    return admin
