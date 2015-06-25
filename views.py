# coding=utf-8
import app_provider
from flask.ext.admin import Admin
from flask.ext.admin.consts import ICON_TYPE_GLYPH
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.model import InlineFormAdmin
from models import *
from wtforms import StringField


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
    column_editable_list = ['name', 'deliver_day', 'lead_day', 'distinguishing_feature',
                            'spec_link', 'purchase_price', 'retail_price']
    column_searchable_list = ('code', 'name', 'supplier.name', 'category.name', 'category.code')
    column_filters = column_searchable_list


class SupplierAdmin(ModelView):
    from models import PaymentMethod
    form_excluded_columns = ('purchaseOrders',)
    inline_models = (PaymentMethod,)
    column_editable_list = ['name', 'qq', 'phone', 'contact', 'email', 'website',
                            'whole_sale_req', 'can_mixed_whole_sale', 'remark']
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

class PurchaseOrderAdmin(ModelView):
    from models import PurchaseOrderLine
    column_list = ('logistic_amount', 'goods_amount', 'total_amount', 'order_date','supplier', 'all_expenses', 'remark')
    form_extra_fields = {
        "goods_amount": StringField('Product Amount'),
        "total_amount": StringField('Total Amount')
    }
    form_widget_args = {
        'goods_amount': {'disabled': True},
        'total_amount': {'disabled': True},
    }
    form_excluded_columns = ('expenses',)

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

    def postprocess_form(self, form):
        form.retail_price = ReadOnlyStringField(label='Retail Price')
        form.price_discount = ReadOnlyStringField(label='Price Discount')
        form.actual_amount = ReadOnlyStringField(label='Actual Amount')
        form.original_amount = ReadOnlyStringField(label='Original Amount')
        form.discount_amount = ReadOnlyStringField(label='Discount Amount')
        return form

class SalesOrderAdmin(ModelView):
    from models import SalesOrderLine
    column_list = ('id', 'logistic_amount','actual_amount', 'original_amount',
                   'discount_amount', 'order_date', 'incoming', 'expense', 'remark')
    column_filters = ('order_date', 'remark', 'logistic_amount')
    form_extra_fields = {
        'actual_amount': StringField('Actual Amount'),
        'original_amount': StringField('Original Amount'),
        'discount_amount': StringField('Discount Amount')
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
    column_labels = dict()
    column_labels['category.display'] = 'Category'
    column_filters = ('date','amount','sales_order.remark', 'category.display')
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
    column_labels = dict()
    column_labels['category.display'] = 'Category'
    column_filters = ('has_invoice','date','amount','category.display',)
    form_excluded_columns = ('sales_order', 'purchase_order',)

class EnumValuesAdmin(ModelView):
    column_list = ('id', 'type', 'code', 'display',)
    column_editable_list = ['display']
    column_searchable_list = ['code', 'display']
    column_filters = ('code', 'display',)

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
        def_so_incoming_type=u'销售单收入默认类型',
        def_so_incoming_status=u'销售单收入默认状态',
        def_so_exp_status=u'销售单物流支出默认状态',
        def_so_exp_type=u'销售单物流支出默认类型',
        def_po_logistic_exp_status=u'采购单物流支出默认状态',
        def_po_logistic_exp_type=u'采购单物流支出默认类型',
        def_po_goods_exp_status=u'采购单货款支出默认状态',
        def_po_goods_exp_type=u'采购单货款支出默认类型',
    )


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
    admin.add_view(PreferenceAdmin(Preference, db_session, category='Settings', name='系统设定', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-cog'))
    return admin
