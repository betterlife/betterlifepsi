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
