# coding=utf-8
from functools import partial
import app_provider
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext, gettext
from models import Preference, Expense, PurchaseOrder, Product
from sqlalchemy import event
from sqlalchemy.orm.attributes import get_history
from views import ModelViewWithAccess, DisabledStringField
from views.base import DeleteValidator
from wtforms import StringField, ValidationError


class PurchaseOrderLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        product=dict(label=lazy_gettext('Product')),
        unit_price=dict(label=lazy_gettext('Unit Price')),
        quantity=dict(label=lazy_gettext('Quantity')),
        remark=dict(label=lazy_gettext('Remark')),
    )

    def postprocess_form(self, form):
        form.total_amount = DisabledStringField(label=lazy_gettext('Total Amount'))
        form.remark = None
        form.inventory_transaction_lines = None
        return form


class PurchaseOrderAdmin(ModelViewWithAccess, DeleteValidator):
    from models import PurchaseOrderLine

    column_list = ('id', 'logistic_amount', 'goods_amount',
                   'total_amount', 'order_date', 'supplier', 'status', 'all_expenses', 'remark')

    form_columns = ('supplier', 'transient_supplier', 'status', 'logistic_amount', 'order_date',
                    'goods_amount', 'total_amount', 'remark', 'lines')
    form_edit_rules = ('transient_supplier', 'status', 'logistic_amount', 'order_date',
                       'goods_amount', 'total_amount', 'remark', 'lines')
    form_create_rules = ('supplier', 'status', 'order_date', 'logistic_amount', 'remark',)

    form_extra_fields = {
        "goods_amount": DisabledStringField(label=lazy_gettext('Goods Amount')),
        "total_amount": DisabledStringField(label=lazy_gettext('Total Amount')),
        'transient_supplier': DisabledStringField(label=lazy_gettext('Supplier'))
    }
    column_sortable_list = ('id', 'logistic_amount', 'total_amount', ('status', 'status.display'),
                            'goods_amount', 'order_date', ('supplier', 'supplier.id'),)
    form_excluded_columns = ('expenses', 'inventory_transactions')
    column_labels = {
        'id': lazy_gettext('id'),
        'logistic_amount': lazy_gettext('Logistic Amount'),
        'order_date': lazy_gettext('Order Date'),
        'supplier': lazy_gettext('Supplier'),
        'remark': lazy_gettext('Remark'),
        'status': lazy_gettext('Status'),
        'all_expenses': lazy_gettext('Related Expenses'),
        'total_amount': lazy_gettext('Total Amount'),
        'goods_amount': lazy_gettext('Goods Amount'),
        'lines': lazy_gettext('Lines'),
    }

    form_args = dict(
        status=dict(query_factory=PurchaseOrder.status_option_filter),
        supplier=dict(description=lazy_gettext('Please select a supplier and save the form, '
                                               'then add purchase order lines accordingly'))
    )

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
        if (logistic_exp is None) and (model.logistic_amount is not None and model.logistic_amount != 0):
            logistic_exp = Expense(model.logistic_amount, model.order_date, preference.def_po_logistic_exp_status_id,
                                   preference.def_po_logistic_exp_type_id)
        if (goods_exp is None) and (model.goods_amount is not None and model.goods_amount != 0):
            goods_exp = Expense(model.goods_amount, model.order_date, preference.def_po_goods_exp_status_id,
                                preference.def_po_goods_exp_type_id)
        if logistic_exp is not None:
            logistic_exp.purchase_order_id = model.id
        if goods_exp is not None:
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

    def edit_form(self, obj=None):
        form = super(ModelView, self).edit_form(obj)
        supplier_id = obj.transient_supplier.id
        # Set query_factory for newly added line
        form.lines.form.product.kwargs['query_factory'] = partial(Product.supplier_filter, supplier_id)
        # Set query option for old lines
        line_entries = form.lines.entries
        products = Product.supplier_filter(supplier_id).all()
        for sub_line in line_entries:
            sub_line.form.product.query = products
        return form

    def on_model_delete(self, model):
        DeleteValidator.validate_status_for_change(model, u'PURCHASE_ORDER_RECEIVED',
                                                   gettext('Purchase order can not be '
                                                           'update nor delete on received status'))

@event.listens_for(PurchaseOrder, 'before_update')
def receive_before_update(mapper, connection, target):
    unchanged_status = get_history(target, 'status')[1]
    if (len(unchanged_status) == 0 and get_history(target, 'status').deleted[0].code == u'PURCHASE_ORDER_RECEIVED') \
            or (len(unchanged_status) > 0 and unchanged_status[0].code == u'PURCHASE_ORDER_RECEIVED'):
        raise ValidationError(gettext('Purchase order can not be update nor delete on received status'))