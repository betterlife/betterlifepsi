import json
from datetime import datetime

from flask_babelex import gettext

from app import const
from app.service import Info
from app.utils import format_util


def amount_and_profit_month(report_type, report_period):
    period = 24
    sql = const.SALES_ORDER_AMOUNT_REPORT_SQL.format('MONTH', "to_char(so.order_date,'Mon')", period)
    results = Info.get_db().engine.execute(sql).fetchall()
    labels, totals = [], []
    for r in results:
        labels.append("{0}, {1}".format(int(r[0]), gettext(r[2])))
        totals.append(float(r[3]))
    average = str(format_util.format_decimal(sum(totals) / float(len(totals))))
    labels.reverse()
    totals.reverse()
    return dict(data={
        "label_average": gettext('Average Sales Amount Per Month(Past {0} Months): {1}').format(period, average),
        "data_average": [average] * len(totals),
        "label": gettext('Total Sales Amount Per Month'),
        "labels": labels, "data": totals}, status='success')


def period_on_period_month(report_type, report_period):
    sql = const.PERIOD_ON_PERIOD_AMOUNT_REPORT_SQL
    results = Info.get_db().engine.execute(sql).fetchall()
    period1, period2 = None, None
    if len(results) >= 1:
        period1 = results[0][2]
    if len(results) >= 2:
        period2 = results[1][2]
    change, result_str = cal_percent_and_change_type(period1, period2)
    return dict(data={
        "data": result_str,
        "change": change
    }, status='success')


def compare_with_last_period_month(report_type, report_period):
    def get_total(year, month):
        sql = const.GET_AMOUNT_BY_MONTH_YEAR.format(month, year)
        results = Info.get_db().engine.execute(sql).fetchall()
        return results[0][0]
    now = datetime.now()
    now = now.replace(month=12, year=2016)
    current_month = now.month
    current_year = now.year
    if current_month == 1:
        last_month = 12
        last_year = now.year - 1
    else:
        last_month = current_month - 1
        last_year = now.year
    total_last_period = get_total(current_year, current_month)
    total_this_period = get_total(last_year, last_month)
    change, result_str = cal_percent_and_change_type(total_this_period, total_last_period)
    return dict(data={
        "data": result_str,
        "change": change
    }, status='success')


def amount_and_profit_week(report_type, report_period):
    period = 52
    sql = const.SALES_ORDER_WEEKLY_AMOUNT_REPORT_SQL.format(period)
    results = Info.get_db().engine.execute(sql).fetchall()
    labels, totals = [], []
    for r in results:
        labels.append("{0}, {1}".format(int(r[0]), gettext(int(r[1]))))
        totals.append(float(r[2]))
    average = str(format_util.format_decimal(sum(totals) / float(len(totals))))
    labels.reverse()
    totals.reverse()
    return dict(data={
        "label_average": gettext('Average Sales Amount Per Week(Past {0} Weeks): {1}').format(period, average),
        "data_average": [average] * len(totals),
        "label": gettext('Total Sales Amount Per Week'),
        "labels": labels, "data": totals}, status='success')


def cal_percent_and_change_type(val_1, val_2):
    if val_1 is not None and val_2 is not None:
        result = (val_1 - val_2) / val_2
        result_str = "{0:.2f}%".format(result)
    else:
        result = 0
        result_str = '-'
    if result < 0:
        change = 'decrease'
    elif result > 0:
        change = 'increase'
    else:
        change = ''
    return change, result_str