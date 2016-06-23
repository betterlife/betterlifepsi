# coding=utf-8
from datetime import datetime
from functools import partial

from app import database
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import FloatSmallerFilter, FloatGreaterFilter, FloatEqualFilter
from flask_admin.model import InlineFormAdmin
from app import const
from flask_babelex import lazy_gettext, gettext
from app.models import Preference, Expense, PurchaseOrder, Product, EnumValues, Receiving
from app.views import ModelViewWithAccess, DisabledStringField
from app.views.base import DeleteValidator
from app.views.formatter import supplier_formatter, expenses_formatter, receivings_formatter, default_date_formatter
from app.utils import form_util


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
        form.pol_receiving_lines = None
        return form


class PurchaseOrderAdmin(ModelViewWithAccess, DeleteValidator):
    from app.models import PurchaseOrderLine

    column_list = ('id', 'order_date', 'supplier', 'logistic_amount', 'goods_amount', 'total_amount',
                   'status', 'all_expenses', 'all_receivings', 'remark')

    column_editable_list = ('remark',)

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
    form_excluded_columns = ('expenses', 'receivings')

    column_details_list = ('id', 'supplier', 'status', 'logistic_amount', 'order_date', 'goods_amount', 'total_amount',
                           'remark', 'lines', 'all_expenses', 'all_receivings')

    column_searchable_list = ('supplier.name', 'status.display', 'remark')

    column_filters = ('order_date', 'supplier.name', 'logistic_amount', 'status.display',
                      FloatSmallerFilter(PurchaseOrder.goods_amount, lazy_gettext('Goods Amount')),
                      FloatGreaterFilter(PurchaseOrder.goods_amount, lazy_gettext('Goods Amount')),
                      FloatEqualFilter(PurchaseOrder.goods_amount, lazy_gettext('Goods Amount')))

    column_labels = {
        'id': lazy_gettext('id'),
        'logistic_amount': lazy_gettext('Logistic Amount'),
        'order_date': lazy_gettext('Order Date'),
        'supplier': lazy_gettext('Supplier'),
        'remark': lazy_gettext('Remark'),
        'status': lazy_gettext('Status'),
        'all_expenses': lazy_gettext('Related Expense'),
        'all_receivings': lazy_gettext('Related Receiving'),
        'total_amount': lazy_gettext('Total Amount'),
        'goods_amount': lazy_gettext('Goods Amount'),
        'lines': lazy_gettext('Lines'),
        'supplier.name': lazy_gettext('Supplier Name'),
        'status.display': lazy_gettext('Status')
    }

    column_formatters = {
        'supplier': supplier_formatter,
        'all_expenses': expenses_formatter,
        'all_receivings': receivings_formatter,
        'order_date': default_date_formatter,
    }

    form_args = dict(
        status=dict(query_factory=PurchaseOrder.status_option_filter,
                    description=lazy_gettext('Purchase order can only be created in draft status, and partially '
                                             'received & received status are driven by associated receiving document')),
        supplier=dict(description=lazy_gettext('Please select a supplier and save the form, '
                                               'then add purchase order lines accordingly')),
        logistic_amount=dict(default=0),
        order_date=dict(default=datetime.now()),
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

    @staticmethod
    def create_receiving_if_not_exist(model):
        """
        Draft receiving document is created from purchase order only
         if there's no associated receiving exists for this PO.
        :param model: the Purchase order model
        :return: Receiving document if a new one created, or None
        """
        receivings = model.po_receivings
        if receivings is None or len(receivings) == 0:
            recv = Receiving.create_draft_recv_from_po(model)
            return recv
        return None

    def after_model_change(self, form, model, is_created):
        logistic_exp, goods_exp = PurchaseOrderAdmin.create_expenses(model)
        db = database.DbInfo.get_db()
        if logistic_exp is not None:
            db.session.add(logistic_exp)
        if goods_exp is not None:
            db.session.add(goods_exp)
        if model.status.code == const.PO_ISSUED_STATUS_KEY:
            receiving = PurchaseOrderAdmin.create_receiving_if_not_exist(model)
            if receiving is not None:
                db.session.add(receiving)
        db.session.commit()

    def edit_form(self, obj=None):
        form = super(ModelView, self).edit_form(obj)
        supplier_id = obj.transient_supplier.id
        # Set query_factory for newly added line
        form.lines.form.product.kwargs['query_factory'] = partial(Product.supplier_filter, supplier_id)
        # Set option list of status available
        if obj.status.code in [const.PO_RECEIVED_STATUS_KEY, const.PO_PART_RECEIVED_STATUS_KEY, const.PO_PART_RECEIVED_STATUS_KEY,
                               const.PO_ISSUED_STATUS_KEY, const.PO_DRAFT_STATUS_KEY]:
            form.status.query = [EnumValues.find_one_by_code(obj.status.code), ]
        if obj.status.code == const.PO_DRAFT_STATUS_KEY:
            form.status.query.append(EnumValues.find_one_by_code(const.PO_ISSUED_STATUS_KEY))
        # Set product query option for old lines(forbid to change product for existing line)
        line_entries = form.lines.entries
        products = Product.supplier_filter(supplier_id).all()
        for sub_line in line_entries:
            sub_line.form.product.query = products
        return form

    def create_form(self, obj=None):
        form = super(ModelView, self).create_form(obj)
        form.status.query = [EnumValues.find_one_by_code(const.PO_DRAFT_STATUS_KEY), ]
        from app.models import Supplier
        form_util.filter_by_organization(form.supplier, Supplier)
        return form

    def on_model_change(self, form, model, is_created):
        super(PurchaseOrderAdmin, self).on_model_change(form, model, is_created)
        DeleteValidator.validate_status_for_change(model, const.PO_RECEIVED_STATUS_KEY,
                                                   gettext('Purchase order can not be update nor delete '
                                                           'on received status'))

    def on_model_delete(self, model):
        DeleteValidator.validate_status_for_change(model, const.PO_RECEIVED_STATUS_KEY,
                                                   gettext('Purchase order can not be '
                                                           'update nor delete on received status'))
