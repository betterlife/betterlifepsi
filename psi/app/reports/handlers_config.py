import json

from flask_babelex import gettext

from psi.app.reports.sales_order_reports import sales_amount_report, \
    compare_period_on_period, compare_with_last_period, sales_profit_report

def dummy_report_function(report_type, report_period):
    return dict(data={
        "message": gettext('Report of type {0} and period {1} was not defined').format(report_type, report_period)
    }, status='error')


report_config = {
    'amount': {
        'month': sales_amount_report,
        'week': sales_amount_report
    },
    'amount_period_on_period': {
        'month': compare_period_on_period,
        'week': compare_period_on_period
    },
    'amount_compare_with_last_period': {
        'month': compare_with_last_period,
        'week': compare_with_last_period,
    },
    'profit': {
        'month': sales_profit_report,
        'week': sales_profit_report
    },
    'profit_period_on_period': {
        'month': compare_period_on_period,
        'week': compare_period_on_period
    },
    'profit_compare_with_last_period': {
        'month': compare_with_last_period,
        'week': compare_with_last_period,
    }

}


