# coding=utf-8
from datetime import datetime

from flask_babelex import gettext

from psi.app.reports import sqls
from psi.app.service import Info
from psi.app.utils import format_util, get_last_week, get_last_month


def sales_amount_report(r_type, r_period):
    limit = get_limit(r_period)
    sql = sqls.SALES_AMOUNT_REPORT_SQL.format('WEEK', 'WW', limit) \
        if r_period == 'week' \
        else sqls.SALES_AMOUNT_REPORT_SQL.format('MONTH', 'Mon', limit)
    results = Info.get_db().engine.execute(sql).fetchall()
    labels, totals = [], []
    for r in results:
        labels.append("{0}, {1}".format(int(r[0]), gettext(r[2])))
        totals.append(float(r[3]))
    avg = str(format_util.format_decimal(sum(totals) / float(len(totals)))) if len(totals) > 0 else 0
    labels.reverse()
    totals.reverse()
    ct = gettext(r_type.capitalize())
    cp = gettext(r_period.capitalize())
    label_tot = gettext('Total Sales {0} Per {1}').format(ct, cp)
    label_avg = gettext('Average Sales {0}(Past {1} {2}(s)): {3}').format(ct, 24, cp, avg)
    return dict(
        data={
            "labels": labels,
            "details": {
                "average_amount": {
                    "label": label_avg,
                    "data": [avg] * len(totals),
                    "style": "average"
                },
                "total": {
                    "label": label_tot,
                    "data": totals,
                    "style": "major"
                }
            }
        },
        status='success'
    )


def compare_period_on_period(r_type, r_period):
    sql = sqls.PERIOD_ON_PERIOD_AMOUNT_REPORT_SQL \
        if r_type == 'amount_period_on_period' \
        else sqls.PERIOD_ON_PERIOD_PROFIT_REPORT_SQL
    sql = sql.format(r_period.capitalize())
    results = Info.get_db().engine.execute(sql).fetchall()
    current, previous = None, None
    if len(results) >= 1:
        current = results[0][2]
    if len(results) >= 2:
        previous = results[1][2]
    change, result_str = cal_percent_and_change_type(current, previous)
    return dict(data={
        "data": result_str,
        "change": change
    }, status='success')


def compare_with_last_period(r_type, r_period):
    now = datetime.now()
    if r_period == 'month':
        current_period = now.month
        current_year = now.year
        last_period, last_year = get_last_month(current_period, current_year)
    elif r_period == 'week':
        current_year, current_period, current_weekday = now.isocalendar()
        last_period, last_year = get_last_week(now)
    else:
        from psi.app.reports.handlers_config import dummy_report_function
        return dummy_report_function(r_type, r_period)
    cap_period = r_period.capitalize()
    last_total = get_total(r_type, cap_period, last_period,last_year)
    this_total = get_total(r_type, cap_period, current_period,current_year)
    change, result_str = cal_percent_and_change_type(this_total, last_total)
    return dict(data={
        "data": result_str,
        "change": change
    }, status='success')


def get_limit(r_period):
    limit = 24 if r_period == 'month' else 53
    return limit

def get_total(report_type, period_type, period_number, year):
    if report_type == 'amount_compare_with_last_period':
        sql = sqls.GET_AMOUNT_BY_YEAR_SQL.format(period_type, period_number, year)
    elif report_type == 'profit_compare_with_last_period':
        sql = sqls.GET_PROFIT_BY_YEAR_SQL.format(period_type, period_number, year)
    results = Info.get_db().engine.execute(sql).fetchall()
    return results[0][0]


def cal_percent_and_change_type(current_val, past_val):
    result_str = None
    result = (current_val - past_val) / past_val \
        if (current_val is not None and past_val is not None and past_val != 0) \
        else 0
    if current_val is None:
        result_str = gettext(u'No Data for this Period')
    elif past_val is None:
        if result_str is not None:
            result_str += gettext(u",") + gettext(u"No Data for previous Period")
        else:
            result_str = gettext(u"No Data for previous Period")
    else:
        result_str = "{0:.2f}%".format(result * 100)
    if result > 0:
        change = 'increase'
    elif result < 0:
        change = 'decrease'
    else:
        change = '-'
    return change, result_str


def sales_profit_report(r_type, r_period):
    limit = get_limit(r_period)
    sql = sqls.SALES_PROFIT_REPORT_SQL.format(r_period, limit)
    labels, profits, totals = [], [], []
    results = Info.get_db().engine.execute(sql).fetchall()

    for r in results:
        labels.append("{0}, {1}".format(int(r[0]), gettext(int(r[1]))))
        totals.append(float(r[2]))
        profits.append(float(r[3]))
    length = len(profits)
    total_avg = str(format_util.format_decimal(sum(totals) / length)) if length > 0 else 0
    profit_avg = str(format_util.format_decimal(sum(profits) / length)) if length > 0 else 0
    label_avg = gettext('Average Sales {0}(Past {1} {2}(s)): {3}')
    label_tot = gettext('Total Sales {0} Per {1}')
    ct = gettext(r_type.capitalize())
    cp = gettext(r_period.capitalize())
    act = gettext("Amount")
    return dict(
        data={
            "labels": labels,
            "details": {
                "average_profit": {
                    "label": label_avg.format(ct, limit, cp, profit_avg),
                    "data": [profit_avg] * length,
                    "style": "average"
                },
                "average_total": {
                    "label": label_avg.format(act, limit, cp, total_avg),
                    "data": [total_avg] * length,
                    "style": "secondary_average"
                },
                "total": {
                    "label": label_tot.format(act, cp),
                    "data": totals,
                    "style": "secondary"
                },
                "profit": {
                    "label": label_tot.format(ct, cp),
                    "data": profits,
                    "style": "major"
                }
            }
        },
        status='success'
    )

