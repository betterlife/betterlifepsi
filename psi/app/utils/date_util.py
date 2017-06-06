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


def get_last_week(the_date):
    """
    Get last ISO week of the date parameter
    :param the_date: the date parameter
    :return: last week and it's year
    """
    current_year, current_week, current_weekday = the_date.isocalendar()
    if current_week == 1:
        last_week = the_date.replace(year=current_year - 1, month=12, day=31)
        last_year = the_date.year - 1
    else:
        last_week = current_week - 1
        last_year = the_date.year
    return last_week, last_year


def get_last_month(month, year):
    """
    Get last month of given month and year
    :param month: given month
    :param year: given year
    :return: last month and it's year
    """
    if month == 1:
        last_month = 12
        last_year = year - 1
    else:
        last_month = month - 1
        last_year = year
    return last_month, last_year


def get_last_quarter(month, year):
    """
    Get last quarter of given month and year
    :param month: given month
    :param year: given year
    :return: last quarter and it's year
    """
    last_quarter = (month-1)//3 
    if last_quarter == 0:
        last_quarter = 4 
        last_year = year - 1
    else:
        last_year = year
    return last_quarter, last_year
