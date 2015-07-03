# coding=utf-8
import app_provider
from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext
from models import Preference, Expense
from views import ModelViewWithAccess, ReadOnlyStringField
from wtforms import StringField

class PurchaseOrderLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        product=dict(label=lazy_gettext('Product')),
        unit_price=dict(label=lazy_gettext('Unit Price')),
        quantity=dict(label=lazy_gettext('Quantity')),
        remark=dict(label=lazy_gettext('Remark')),
    )

    def postprocess_form(self, form):
        form.total_amount = ReadOnlyStringField(label=lazy_gettext('Total Amount'))
        return form


class PurchaseOrderAdmin(ModelViewWithAccess):
    from models import PurchaseOrderLine

    column_list = ('id', 'logistic_amount', 'goods_amount',
                   'total_amount', 'order_date', 'supplier', 'all_expenses', 'remark')

    form_extra_fields = {
        "goods_amount": StringField(label=lazy_gettext('Goods Amount')),
        "total_amount": StringField(label=lazy_gettext('Total Amount')),
    }
    column_sortable_list = ('id', 'logistic_amount', 'total_amount',
                            'goods_amount', 'order_date', ('supplier', 'supplier.id'),)
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
