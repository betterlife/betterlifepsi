# encoding=utf-8
from datetime import datetime


def years_ago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    try:
        return from_date.replace(year=from_date.year - years)
    except ValueError:
        # Must be 2/29!
        assert from_date.month == 2 and from_date.day == 29
        return from_date.replace(month=2, day=28,
                                 year=from_date.year - years)


def num_years(begin, end=None):
    if end is None:
        end = datetime.now()
    num_of_years = int((end - begin).days / 365.25)
    if begin > years_ago(num_of_years, end):
        return num_of_years - 1
    else:
        return num_of_years


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