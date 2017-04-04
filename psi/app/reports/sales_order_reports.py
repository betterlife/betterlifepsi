from datetime import datetime

from flask_babelex import gettext

from app import const
from app.service import Info
from app.utils import format_util, get_last_week, get_last_month


def sales_amount_report(r_type, r_period):
    if r_period == 'month':
        sql = const.SALES_ORDER_AMOUNT_REPORT_SQL.format('MONTH',
                                                         "to_char(so.order_date,'Mon')",
                                                         24)
    else:
        sql = const.SALES_ORDER_AMOUNT_REPORT_SQL.format('WEEK',
                                                         "to_char(so.order_date,'WW')",
                                                         53)
    results = Info.get_db().engine.execute(sql).fetchall()
    labels, totals = [], []
    for r in results:
        labels.append("{0}, {1}".format(int(r[0]), gettext(r[2])))
        totals.append(float(r[3]))
    average = str(format_util.format_decimal(sum(totals) / float(len(totals))))
    labels.reverse()
    totals.reverse()
    ct = gettext(r_type.capitalize())
    cp = gettext(r_period.capitalize())
    label_tot = gettext('Total Sales {0} Per {1}').format(ct, cp)
    label_avg = gettext('Average Sales {0}(Past {1} {2}(s)): {3}').format(ct, 24, cp, average)
    return dict(
        data={
            "labels": labels,
            "details": {
                "average_amount": {
                    "label": label_avg,
                    "data": [average] * len(totals),
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


def compare_amount_period_on_period(report_type, report_period):
    sql = const.PERIOD_ON_PERIOD_AMOUNT_REPORT_SQL.format(
        report_period.capitalize())
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


def compare_amount_with_last_period(report_type, report_period):
    now = datetime.now()
    if report_period == 'month':
        current_period = now.month
        current_year = now.year
        last_period, last_year = get_last_month(current_period, current_year)
    elif report_period == 'week':
        current_year, current_period, current_weekday = now.isocalendar()
        last_period, last_year = get_last_week(now)
    else:
        from app.reports.handlers_config import dummy_report_function
        return dummy_report_function(report_type, report_period)
    total_last_period = get_total(report_period.capitalize(), last_period,
                                  last_year)
    total_this_period = get_total(report_period.capitalize(), current_period,
                                  current_year)
    change, result_str = cal_percent_and_change_type(total_this_period,
                                                     total_last_period)
    return dict(data={
        "data": result_str,
        "change": change
    }, status='success')


def get_total(period_type, period_number, year):
    sql = const.GET_AMOUNT_BY_PERIOD_YEAR.format(period_type, period_number,
                                                 year)
    results = Info.get_db().engine.execute(sql).fetchall()
    return results[0][0]


def cal_percent_and_change_type(current_val, past_val):
    result = (current_val - past_val) / past_val if (
        current_val is not None and past_val is not None) else 0
    result_str = "{0:.2f}%".format(result * 100) if (
        current_val is not None and past_val is not None) else '-'
    if result > 0:
        change = 'increase'
    elif result < 0:
        change = 'decrease'
    else:
        change = '-'
    return change, result_str


def sales_profit_report(r_type, r_period):
    if (r_period == 'month'):
        limit = 24
    else:
        limit = 53
    sql = const.SALES_PROFIT_REPORT_SQL.format(r_period, limit)
    labels, profits, totals = [], [], []
    results = Info.get_db().engine.execute(sql).fetchall()

    for r in results:
        labels.append("{0}, {1}".format(int(r[0]), gettext(int(r[1]))))
        totals.append(float(r[2]))
        profits.append(float(r[3]))
    length = len(profits)
    total_avg = str(format_util.format_decimal(sum(totals) / length))
    profit_avg = str(format_util.format_decimal(sum(profits) / length))
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
