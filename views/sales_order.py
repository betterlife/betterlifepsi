# coding=utf-8
from datetime import datetime
import app_provider
from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext
from models import Preference, Incoming, Expense
from views import ModelViewWithAccess, DisabledStringField
from wtforms import StringField

class SalesOrderLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        product=dict(label=lazy_gettext('Product')),
        unit_price=dict(label=lazy_gettext('Unit Price')),
        quantity=dict(label=lazy_gettext('Quantity')),
        remark=dict(label=lazy_gettext('Remark')),
    )

    def postprocess_form(self, form):
        form.retail_price = DisabledStringField(label=lazy_gettext('Retail Price'))
        form.price_discount = DisabledStringField(label=lazy_gettext('Price Discount'))
        form.original_amount = DisabledStringField(label=lazy_gettext('Original Amount'))
        form.actual_amount = DisabledStringField(label=lazy_gettext('Actual Amount'))
        form.discount_amount = DisabledStringField(label=lazy_gettext('Discount Amount'))
        form.remark = None
        form.sol_shipping_lines = None
        return form


class SalesOrderAdmin(ModelViewWithAccess):
    from models import SalesOrderLine

    column_list = ('id', 'logistic_amount', 'actual_amount', 'original_amount',
                   'discount_amount', 'order_date', 'incoming', 'expense', 'so_shippings', 'remark')
    # column_filters = ('order_date', 'remark', 'logistic_amount')
    form_extra_fields = {
        'actual_amount': DisabledStringField(label=lazy_gettext('Actual Amount')),
        'original_amount': DisabledStringField(label=lazy_gettext('Original Amount')),
        'discount_amount': DisabledStringField(label=lazy_gettext('Discount Amount'))
    }
    form_args = dict(
        logistic_amount=dict(default=0),
        order_date=dict(default=datetime.now())
    )
    form_excluded_columns = ('incoming', 'expense', 'so_shippings')
    column_sortable_list = ('id', 'logistic_amount', 'actual_amount',
                            'original_amount', 'discount_amount', 'order_date')
    inline_models = (SalesOrderLineInlineAdmin(SalesOrderLine),)

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
        'so_shippings': lazy_gettext('Related Shipping'),
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
            default_obj = Expense(model.logistic_amount, model.order_date,
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
