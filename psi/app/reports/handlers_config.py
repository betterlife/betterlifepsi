import json

from flask_admin.babel import gettext

from app.reports.sales_order_reports import amount_month, amount_week, period_on_period, \
    compare_with_last_period


def dummy_report_function(report_type, report_period):
    return dict(data={
        "message": gettext('Report of type {0} and period {1} is not defined').format(report_type, report_period)
    }, status='error')


report_config = {
    'amount': {
        'month': amount_month,
        'week': amount_week
    },
    'amount_period_on_period': {
        'month': period_on_period,
        'week': period_on_period
    },
    'amount_compare_with_last_period': {
        'month': compare_with_last_period,
        'week': compare_with_last_period,
    }
}


