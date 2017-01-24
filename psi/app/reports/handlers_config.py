import json

from flask_admin.babel import gettext

from app.reports.sales_order_reports import amount_and_profit_month, amount_and_profit_week, period_on_period_month, \
    compare_with_last_period_month


def dummy_report_function(report_type, report_period):
    return dict(data={
        "label": gettext('Report of type {0} and period {1} is not defined', report_type, report_period)
    }, status='error')


report_config = {
    'amount_and_profit': {
        'month': amount_and_profit_month,
        'week': amount_and_profit_week
    },
    'period_on_period': {
        'month': period_on_period_month,
        'week': dummy_report_function
    },
    'compare_with_last_period': {
        'month': compare_with_last_period_month,
        'week': dummy_report_function
    },
}


