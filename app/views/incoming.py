# coding=utf-8
from datetime import datetime

from flask.ext.babelex import lazy_gettext
from app.models import Incoming
from app.views import ModelViewWithAccess
from formatter import sales_order_formatter, default_date_formatter


class IncomingAdmin(ModelViewWithAccess):
    column_list = ('id', 'date', 'amount', 'status', 'category', 'sales_order', 'remark')
    column_editable_list = ['date', 'amount', 'remark']

    edit_modal = True
    create_modal = True

    form_args = dict(
        status=dict(query_factory=Incoming.status_filter),
        category=dict(query_factory=Incoming.type_filter),
        date=dict(default=datetime.now()),
    )
    column_sortable_list = ('id', 'date', 'amount', ('status', 'status.display'),
                            ('category', 'category.display'), 'remark')
    column_labels = {
        'id': lazy_gettext('id'),
        'amount': lazy_gettext('Amount'),
        'date': lazy_gettext('Date'),
        'category': lazy_gettext('Category'),
        'status': lazy_gettext('Status'),
        'sales_order': lazy_gettext('Related Sales Order'),
        'remark': lazy_gettext('Remark'),
        'category.display': lazy_gettext('Category'),
    }
    # column_filters = ('date','amount','sales_order.remark', 'category.display')
    form_excluded_columns = ('sales_order',)
    column_formatters = {
        'sales_order': sales_order_formatter,
        'date': default_date_formatter,
    }