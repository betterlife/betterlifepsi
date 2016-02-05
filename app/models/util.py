from decimal import Decimal, ROUND_HALF_UP
import datetime


def format_decimal(value):
    return Decimal(Decimal(value).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))


def get_weeks_between(d1, d2):
    """
    Calculating the difference in weeks between the Mondays within weeks of respective dates

    :param d1: day one, the start date
    :param d2: day two, the end date
    :return: Returns 0 if both dates fall withing one week, 1 if on two consecutive weeks, etc.
    """
    from datetime import timedelta
    if d1 is None or d2 is None:
        return 1
    monday1 = (d1 - timedelta(days=d1.weekday()))
    monday2 = (d2 - timedelta(days=d2.weekday()))
    return (monday2 - monday1).days / 7
