# coding=utf-8
from datetime import datetime
from flask.ext.babelex import lazy_gettext
from models import Expense
from views import ModelViewWithAccess
from formatter import sales_order_formatter, purchase_order_formatter, default_date_formatter


class ExpenseAdmin(ModelViewWithAccess):
    column_list = ('id', 'date', 'amount', 'has_invoice', 'status',
                   'category', 'purchase_order', 'sales_order', 'remark')
    column_editable_list = ['date', 'amount', 'has_invoice', 'remark']

    form_args = dict(
        status=dict(query_factory=Expense.status_filter),
        category=dict(query_factory=Expense.type_filter),
        date=dict(default=datetime.now()),
    )
    column_sortable_list = ('id', 'date', 'amount', 'has_invoice', ('status', 'status.display'),
                            ('category', 'category.display'), 'remark')
    column_labels = {
        'id': lazy_gettext('id'),
        'amount': lazy_gettext('Amount'),
        'date': lazy_gettext('Date'),
        'category': lazy_gettext('Category'),
        'status': lazy_gettext('Status'),
        'sales_order': lazy_gettext('Related Sales Order'),
        'purchase_order': lazy_gettext('Related Purchase Order'),
        'remark': lazy_gettext('Remark'),
        'category.display': lazy_gettext('Category'),
        'has_invoice': lazy_gettext('Has Invoice'),
    }
    # column_filters = ('has_invoice','date','amount','category.display',)
    form_excluded_columns = ('sales_order', 'purchase_order',)

    column_formatters = {
        'sales_order': sales_order_formatter,
        'purchase_order': purchase_order_formatter,
        'date': default_date_formatter,
    }
