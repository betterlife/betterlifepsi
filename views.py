# coding=utf-8
import app_provider
from flask.ext.admin import Admin
from flask.ext.admin.consts import ICON_TYPE_GLYPH
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext
from models import *
from wtforms import StringField


class ProductCategoryAdmin(ModelView):
    column_exclude_list = ['sub_categories', 'products']
    column_sortable_list = ('code', 'name')
    column_searchable_list = ('code', 'name')
    # column_filters = ('code','name')
    column_editable_list = ['code', 'name']
    column_labels = {
        'id': lazy_gettext('id'),
        'name': lazy_gettext('Name'),
        'code': lazy_gettext('Code'),
        'parent_category': lazy_gettext('Parent category'),
    }
    form_excluded_columns = ('sub_categories','products')


class ProductAdmin(ModelView):
    column_editable_list = ['name', 'deliver_day', 'lead_day', 'distinguishing_feature',
                            'spec_link', 'purchase_price', 'retail_price']
    column_searchable_list = ('code', 'name', 'supplier.name', 'category.name', 'category.code')
    # column_filters = column_searchable_list
    column_labels = {
        'supplier.name': lazy_gettext('Supplier Name'),
        'category.name': lazy_gettext('Category Name'),
        'category.code': lazy_gettext('Category Code'),
        'supplier': lazy_gettext('Supplier'),
        'name': lazy_gettext('Name'),
        'code': lazy_gettext('Code'),
        'category': lazy_gettext('Category'),
        'deliver_day': lazy_gettext('Deliver Day'),
        'lead_day': lazy_gettext('Lead Day'),
        'distinguishing_feature': lazy_gettext('Distinguishing Feature'),
        'spec_link': lazy_gettext('Spec Link'),
        'purchase_price': lazy_gettext('Purchase Price'),
        'retail_price': lazy_gettext('Retail Price')
    }

class PaymentMethodLineInlineAdmin(InlineFormAdmin):
    # column_editable_list = ['account_name', 'account_number', 'bank_name', 'bank_branch', 'remark']
    form_args = dict(
        account_name=dict(label=lazy_gettext('Account Name')),
        account_number=dict(label=lazy_gettext('Account Number')),
        bank_name=dict(label=lazy_gettext('Bank Name')),
        bank_branch=dict(label=lazy_gettext('Bank Branch')),
        remark=dict(label=lazy_gettext('Remark')),
    )

class SupplierAdmin(ModelView):
    from models import PaymentMethod
    form_excluded_columns = ('purchaseOrders','products')
    inline_models = (PaymentMethodLineInlineAdmin(PaymentMethod),)
    column_editable_list = ['name', 'qq', 'phone', 'contact', 'email', 'website',
                            'whole_sale_req', 'can_mixed_whole_sale', 'remark']
    column_searchable_list = ('code', 'name')
    # column_filters = column_searchable_list
    column_labels = {
        'id': lazy_gettext('id'),
        'name': lazy_gettext('Name'),
        'code': lazy_gettext('Code'),
        'qq': lazy_gettext('QQ'),
        'phone': lazy_gettext('Phone'),
        'contact': lazy_gettext('Contact'),
        'email': lazy_gettext('Email'),
        'website': lazy_gettext('Website'),
        'whole_sale_req': lazy_gettext('Whole Sale Req'),
        'can_mixed_whole_sale': lazy_gettext('Can Mixed Whole Sale'),
        'remark': lazy_gettext('Remark'),
        'paymentMethods': lazy_gettext('Payment Methods'),
    }

class ReadOnlyStringField(StringField):
    def __call__(self, **kwargs):
        kwargs['disabled'] = True
        return super(ReadOnlyStringField, self).__call__(**kwargs)

class PurchaseOrderLineInlineAdmin(InlineFormAdmin):
    form_args=dict(
        product=dict(label=lazy_gettext('Product')),
        unit_price=dict(label=lazy_gettext('Unit Price')),
        quantity=dict(label=lazy_gettext('Quantity')),
        remark=dict(label=lazy_gettext('Remark')),
    )
    def postprocess_form(self, form):
        form.total_amount = ReadOnlyStringField(label=lazy_gettext('Total Amount'))
        return form

class PurchaseOrderAdmin(ModelView):
    from models import PurchaseOrderLine
    column_list = ('id', 'logistic_amount', 'goods_amount', 'total_amount', 'order_date','supplier', 'all_expenses', 'remark')
    form_extra_fields = {
        "goods_amount": StringField(label=lazy_gettext('Goods Amount')),
        "total_amount": StringField(label=lazy_gettext('Total Amount')),
    }
    form_widget_args = {
        'goods_amount': {'disabled': True},
        'total_amount': {'disabled': True},
    }
    form_excluded_columns = ('expenses',)
    column_labels = {
        'id': lazy_gettext('id'),
        'logistic_amount': lazy_gettext('Logistic Amount'),
        'order_date': lazy_gettext('Order Date'),
        'supplier': lazy_gettext('Supplier'),
        'remark': lazy_gettext('Remark'),
        'all_expenses': lazy_gettext('Related Expenses'),
        'total_amount': lazy_gettext('Total Amount'),
        'goods_amount': lazy_gettext('Goods Amount'),
        'lines': lazy_gettext('Lines'),
    }

    @staticmethod
    def create_expenses(model):
        expenses = model.expenses
        logistic_exp = None
        preference = Preference.get()
        goods_exp = None
        if expenses is None:
            expenses = dict()
        for expense in expenses:
            if (expense.category_id == preference.def_po_logistic_exp_type_id) and (model.logistic_amount != 0):
                logistic_exp = expense
                logistic_exp.amount = model.logistic_amount
            elif (expense.category_id == preference.def_po_goods_exp_type_id) and (model.goods_amount != 0):
                goods_exp = expense
                goods_exp.amount = model.goods_amount
        if (logistic_exp is None) and (model.logistic_amount != 0):
            logistic_exp = Expense(model.logistic_amount, model.order_date, preference.def_po_logistic_exp_status_id,
                                   preference.def_po_logistic_exp_type_id)
        if (goods_exp is None) and (model.goods_amount != 0):
            goods_exp = Expense(model.goods_amount, model.order_date, preference.def_po_goods_exp_status_id,
                                preference.def_po_goods_exp_type_id)
        logistic_exp.purchase_order_id = model.id
        goods_exp.purchase_order_id = model.id
        return logistic_exp, goods_exp

    inline_models = (PurchaseOrderLineInlineAdmin(PurchaseOrderLine),)

    def after_model_change(self, form, model, is_created):
        logistic_exp, goods_exp = PurchaseOrderAdmin.create_expenses(model)
        if logistic_exp is not None:
            app_provider.AppInfo.get_db().session.add(logistic_exp)
        if goods_exp is not None:
            app_provider.AppInfo.get_db().session.add(goods_exp)
        app_provider.AppInfo.get_db().session.commit()

class SalesOrderLineInlineAdmin(InlineFormAdmin):

    form_args=dict(
        product=dict(label=lazy_gettext('Product')),
        unit_price=dict(label=lazy_gettext('Unit Price')),
        quantity=dict(label=lazy_gettext('Quantity')),
        remark=dict(label=lazy_gettext('Remark')),
    )

    def postprocess_form(self, form):
        form.retail_price = ReadOnlyStringField(label=lazy_gettext('Retail Price'))
        form.price_discount = ReadOnlyStringField(label=lazy_gettext('Price Discount'))
        form.original_amount = ReadOnlyStringField(label=lazy_gettext('Original Amount'))
        form.actual_amount = ReadOnlyStringField(label=lazy_gettext('Actual Amount'))
        form.discount_amount = ReadOnlyStringField(label=lazy_gettext('Discount Amount'))
        return form

class SalesOrderAdmin(ModelView):
    from models import SalesOrderLine
    column_list = ('id', 'logistic_amount','actual_amount', 'original_amount',
                   'discount_amount', 'order_date', 'incoming', 'expense', 'remark')
    # column_filters = ('order_date', 'remark', 'logistic_amount')
    form_extra_fields = {
        'actual_amount': StringField(label=lazy_gettext('Actual Amount')),
        'original_amount': StringField(label=lazy_gettext('Original Amount')),
        'discount_amount': StringField(label=lazy_gettext('Discount Amount'))
    }
    form_widget_args = {
        'actual_amount': {'disabled': True},
        'original_amount': {'disabled': True},
        'discount_amount': {'disabled': True},
        'logistic_amount': {'default': 0}
    }
    form_excluded_columns = ('incoming', 'expense')
    column_sortable_list = ('logistic_amount', 'actual_amount', 'original_amount', 'discount_amount', 'order_date')
    inline_models = (SalesOrderLineInlineAdmin(SalesOrderLine),)

    column_labels = {
        'id': lazy_gettext('id'),
        'logistic_amount': lazy_gettext('Logistic Amount'),
        'order_date': lazy_gettext('Order Date'),
        'remark': lazy_gettext('Remark'),
        'actual_amount': lazy_gettext('Actual Amount'),
        'original_amount': lazy_gettext('Original Amount'),
        'discount_amount': lazy_gettext('Discount Amount'),
        'incoming': lazy_gettext('Relate Incoming'),
        'expense': lazy_gettext('Relate Expense'),
        'lines': lazy_gettext('Lines'),
    }

    @staticmethod
    def create_incoming(model):
        incoming = model.incoming
        preference = Preference.get()
        incoming = SalesOrderAdmin.create_associated_obj(incoming, model, default_obj=Incoming(),
                                                         value=model.actual_amount,
                                                         status_id=preference.def_so_incoming_status_id,
                                                         type_id=preference.def_so_incoming_type_id)
        return incoming

    @staticmethod
    def create_expense(model):
        expense = model.expense
        preference = Preference.get()
        if (model.logistic_amount is not None) and (model.logistic_amount > 0):
            default_obj=Expense(model.logistic_amount, model.order_date,
                                preference.def_so_exp_status_id, preference.def_so_exp_type_id)
            expense = SalesOrderAdmin.create_associated_obj(expense, model,
                                                            default_obj=default_obj,
                                                            value=model.logistic_amount,
                                                            status_id=preference.def_so_exp_status_id,
                                                            type_id=preference.def_so_exp_type_id)
        return expense

    @staticmethod
    def create_associated_obj(obj, model, default_obj, value, status_id, type_id):
        if obj is None:
            obj = default_obj
            obj.status_id = status_id
            obj.category_id = type_id
        obj.amount = value
        obj.sales_order_id = model.id
        obj.date = model.order_date
        return obj

    def after_model_change(self, form, model, is_created):
        incoming = SalesOrderAdmin.create_incoming(model)
        expense = SalesOrderAdmin.create_expense(model)
        if expense is not None:
            app_provider.AppInfo.get_db().session.add(expense)
        if incoming is not None:
            app_provider.AppInfo.get_db().session.add(incoming)
        app_provider.AppInfo.get_db().session.commit()


class IncomingAdmin(ModelView):
    column_list = ('id', 'date', 'amount', 'status', 'category', 'sales_order', 'remark')
    column_editable_list = ['date', 'amount',]
    form_args = dict(
        status=dict(query_factory=Incoming.status_filter),
        category=dict(query_factory=Incoming.type_filter),
    )
    column_labels = {
        'id': lazy_gettext('id'),
        'amount': lazy_gettext('Amount'),
        'date': lazy_gettext('Date'),
        'category': lazy_gettext('Category'),
        'status': lazy_gettext('Status'),
        'sales_order': lazy_gettext('Relate Sales Order'),
        'remark': lazy_gettext('Remark'),
        'category.display': lazy_gettext('Category'),
    }
    # column_filters = ('date','amount','sales_order.remark', 'category.display')
    form_excluded_columns = ('sales_order',)

class ExpenseAdmin(ModelView):
    column_list = ('id', 'date', 'amount', 'has_invoice', 'status',
                   'category', 'purchase_order', 'sales_order', 'remark')
    column_editable_list = ['date', 'amount', 'has_invoice',]
    form_args = dict(
        status=dict(query_factory=Expense.status_filter),
        category=dict(query_factory=Expense.type_filter),
    )
    column_sortable_list=('date','amount','has_invoice',('status','status.display'),
                          ('category', 'category.display'),'remark')
    column_labels = {
        'id': lazy_gettext('id'),
        'amount': lazy_gettext('Amount'),
        'date': lazy_gettext('Date'),
        'category': lazy_gettext('Category'),
        'status': lazy_gettext('Status'),
        'sales_order': lazy_gettext('Relate Sales Order'),
        'purchase_order': lazy_gettext('Relate Purchase Order'),
        'remark': lazy_gettext('Remark'),
        'category.display': lazy_gettext('Category'),
        'has_invoice': lazy_gettext('Has Invoice'),
    }
    # column_filters = ('has_invoice','date','amount','category.display',)
    form_excluded_columns = ('sales_order', 'purchase_order',)

class EnumValuesAdmin(ModelView):
    column_list = ('id', 'type', 'code', 'display',)
    column_editable_list = ['display']
    column_searchable_list = ['code', 'display']
    # column_filters = ('code', 'display',)
    column_labels = {
        'id': lazy_gettext('id'),
        'type': lazy_gettext('Type'),
        'code': lazy_gettext('Code'),
        'display': lazy_gettext('Display'),
    }

class PreferenceAdmin(ModelView):
    can_create, can_delete = False, False
    form_args = dict(
        def_so_incoming_type=dict(query_factory=Incoming.type_filter),
        def_so_incoming_status=dict(query_factory=Incoming.status_filter),
        def_so_exp_status=dict(query_factory=Expense.status_filter),
        def_so_exp_type=dict(query_factory=Expense.type_filter),
        def_po_logistic_exp_status=dict(query_factory=Expense.status_filter),
        def_po_logistic_exp_type=dict(query_factory=Expense.type_filter),
        def_po_goods_exp_status=dict(query_factory=Expense.status_filter),
        def_po_goods_exp_type=dict(query_factory=Expense.type_filter),
    )
    column_list = ('def_so_incoming_type', 'def_so_incoming_status',
                   'def_so_exp_status', 'def_so_exp_type',
                   'def_po_logistic_exp_status','def_po_logistic_exp_type',
                   'def_po_goods_exp_status','def_po_goods_exp_type')
    column_labels = dict(
        def_so_incoming_type=lazy_gettext('Default Sales Order Incoming Type'),
        def_so_incoming_status=lazy_gettext('Default Sale Order Incoming Status'),
        def_so_exp_status=lazy_gettext('Default Sale Order Expense Status'),
        def_so_exp_type=lazy_gettext('Default Sales Order Expense Type'),
        def_po_logistic_exp_status=lazy_gettext('Default Purchase Order Logistic Expense Status'),
        def_po_logistic_exp_type=lazy_gettext('Default Purchase Order Logistic Expense Type'),
        def_po_goods_exp_status=lazy_gettext('Default Purchase Order Goods Expense Status'),
        def_po_goods_exp_type=lazy_gettext('Default Purchase Order Goods Expense Type'),
        remark=lazy_gettext('Remark'),
    )

def init_admin_views(app, db):
    db_session = db.session
    admin = Admin(app, lazy_gettext('Brand Name'), base_template='layout.html', template_mode='bootstrap3')
    admin.add_view(PurchaseOrderAdmin(PurchaseOrder, db_session, name=lazy_gettext("Purchase Order"),
                                      menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-shopping-cart'))
    admin.add_view(SalesOrderAdmin(SalesOrder, db_session, name=lazy_gettext("Sales Order"),
                                   menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-send'))
    admin.add_view(ExpenseAdmin(Expense, db_session, name=lazy_gettext("Expense"),
                                menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-usd'))
    admin.add_view(IncomingAdmin(Incoming, db_session, name=lazy_gettext("Incoming"),
                                 menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-minus-sign'))
    admin.add_view(ProductAdmin(Product, db_session, name=lazy_gettext("Product"),
                                category=u'基础信息', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-barcode'))
    admin.add_view(SupplierAdmin(Supplier, db_session,name=lazy_gettext("Supplier"),
                                 category=u'基础信息', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-globe'))
    admin.add_view(ProductCategoryAdmin(ProductCategory, db_session, name=lazy_gettext("Product Category"),
                                        category=u'基础信息', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tags'))
    admin.add_view(EnumValuesAdmin(EnumValues, db_session, name=lazy_gettext("Enum Values"),
                                   category=u'基础信息', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tasks'))
    admin.add_view(PreferenceAdmin(Preference, db_session, name=lazy_gettext("Preference"),
                                   category=u'基础信息',  menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-cog'))
    return admin
