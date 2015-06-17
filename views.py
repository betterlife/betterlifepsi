from database import db_session
from flask.ext.admin.contrib.sqla import ModelView
from models import EnumValues, PaymentMethod, PurchaseOrderLine, SalesOrderLine, Product


class ProductCategoryAdmin(ModelView):
    column_exclude_list = ['sub_categories', 'products']

    column_sortable_list = ('code', 'name')

    # Full text search
    column_searchable_list = ('code', 'name')

    # Column filters
    column_filters = ('code','name')

    column_editable_list = ['code', 'name']

    form_widget_args = {
        'sub_categories': { 'disabled': True },
        'products' : { 'disabled' : True },
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
    inline_models = (PaymentMethod, Product)
    column_editable_list = ['name', 'qq', 'phone', 'contact', 'email', 'website', 'whole_sale_req', 'can_mixed_whole_sale', 'remark']
    column_searchable_list = ('code', 'name')
    column_filters = column_searchable_list


class PaymentMethodAdmin(ModelView):
    column_editable_list = ['account_name', 'account_number', 'bank_name', 'bank_branch', 'remark']

class PurchaseOrderAdmin(ModelView):
    inline_models = (PurchaseOrderLine,)

class SalesOrderAdmin(ModelView):
    inline_models = (SalesOrderLine,)

def filtering_function():
    return db_session.query(EnumValues).filter_by(code='EXPENSE_TYPE')

class ExpenseAdmin(ModelView):

    form_args = dict(
        status = dict(label='Status', query_factory=filtering_function)
    )

class EnumValuesAdmin(ModelView):
    form_widget_args = {
        'type_values': {
            'disabled': True
        }
    }
    column_editable_list = ['display']
    column_searchable_list = ['code', 'display']
    column_filters = ('code', 'display',)

