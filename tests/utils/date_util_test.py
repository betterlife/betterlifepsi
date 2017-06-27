# encoding=utf-8
import unittest
from datetime import datetime, date, time, timedelta

from psi.app.utils import date_util


class TestDateUtil(unittest.TestCase):
    def test_num_years(self):
        begin = datetime.combine(date(2014, 6, 24), time(12, 30))
        years = date_util.num_years(begin)
        year_num = datetime.now().year - 2014
        self.assertEqual(year_num, years)
        begin = datetime.combine(date(2000, 6, 24), time(12, 30))
        year_num = datetime.now().year - 2000
        self.assertEqual(year_num, date_util.num_years(begin))
        end = datetime.combine(date(2016, 6, 24), time(12, 30))
        self.assertEqual(16, date_util.num_years(begin, end), years)

    def test_get_last_quarter(self):
        test_date = datetime(2014,12,31)

        last_q, last_y = date_util.get_last_quarter(test_date.month, test_date.year)
        self.assertEqual(3, last_q)
        self.assertEqual(2014, last_y)

        test_date = datetime(2005,3,30)
        last_q, last_y = date_util.get_last_quarter(test_date.month, test_date.year)
        self.assertEqual(4, last_q)
        self.assertEqual(2004, last_y)

        test_date = datetime(2005,1,1)
        last_q, last_y = date_util.get_last_quarter(test_date.month, test_date.year)
        self.assertEqual(4, last_q)
        self.assertEqual(2004, last_y)

    def test_get_last_month(self):
        test_date = datetime(2014,12,31)
        last_m,last_y = date_util.get_last_month(test_date.month, test_date.year)
        self.assertEqual(11, last_m)
        self.assertEqual(2014, last_y)

        test_date = datetime(2014,1,31)
        last_m,last_y = date_util.get_last_month(test_date.month, test_date.year)
        self.assertEqual(12, last_m)
        self.assertEqual(2013, last_y)
