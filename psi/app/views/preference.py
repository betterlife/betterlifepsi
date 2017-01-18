# coding=utf-8
from psi.app.models import Incoming, Expense
from flask_babelex import lazy_gettext

from psi.app.views.base import ModelViewWithAccess


class PreferenceAdmin(ModelViewWithAccess):
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
                   'def_po_logistic_exp_status', 'def_po_logistic_exp_type',
                   'def_po_goods_exp_status', 'def_po_goods_exp_type')
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
