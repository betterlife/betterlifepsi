from database import db_session
from flask.ext.admin.contrib.sqla import ModelView
from models import EnumValues, PaymentMethod, PurchaseOrderLine, SalesOrderLine, Product


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
    form_excluded_columns = ('purchaseOrders',)
    inline_models = (PaymentMethod,)
    column_editable_list = ['name', 'qq', 'phone', 'contact', 'email', 'website', 'whole_sale_req', 'can_mixed_whole_sale', 'remark']
    column_searchable_list = ('code', 'name')
    column_filters = column_searchable_list


class PaymentMethodAdmin(ModelView):
    column_editable_list = ['account_name', 'account_number', 'bank_name', 'bank_branch', 'remark']

class PurchaseOrderAdmin(ModelView):
    inline_models = (PurchaseOrderLine,)

class SalesOrderAdmin(ModelView):
    inline_models = (SalesOrderLine,)

def expense_status_filter():
    return enum_type_filter('EXP_STATUS')

def expense_type_filter():
    return enum_type_filter('EXP_TYPE')

def incoming_status_filter():
    return enum_type_filter('INCOMING_STATUS')

def incoming_type_filter():
    return enum_type_filter('INCOMING_TYPE')

def enum_type_filter(type_code):
    return db_session.query(EnumValues).\
        join(EnumValues.type, aliased=True).\
        filter_by(code=type_code)

class IncomingAdmin(ModelView):
    form_args = dict(
        status = dict(query_factory=incoming_status_filter),
        category = dict(query_factory=incoming_type_filter),
    )

class ExpenseAdmin(ModelView):
    form_args = dict(
        status = dict(query_factory=expense_status_filter),
        category = dict(query_factory=expense_type_filter),
    )

class EnumValuesAdmin(ModelView):
    column_editable_list = ['display']
    column_searchable_list = ['code', 'display']
    column_filters = ('code', 'display',)

