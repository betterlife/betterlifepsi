# encoding=utf-8
import unittest
from datetime import datetime, date, time, timedelta

from app.utils import date_util


class TestCases(unittest.TestCase):
    def test_get_weeks_between(self):
        d1, d2 = None, datetime.now()
        self.assertEqual(1, date_util.get_weeks_between(d1, d2))
        d1 = datetime.now() - timedelta(days=5)
        self.assertEqual(0, date_util.get_weeks_between(d1, d2))

        d1 = d1 - timedelta(days=7)
        self.assertEqual(1, date_util.get_weeks_between(d1, d2))

        d1 = d2 - timedelta(days=14)
        self.assertEqual(2, date_util.get_weeks_between(d1, d2))

    def test_num_years(self):
        begin = datetime.combine(date(2014, 06, 24), time(12, 30))
        years = date_util.num_years(begin)
        self.assertEqual(1, years)
        begin = datetime.combine(date(2000, 06, 24), time(12, 30))
        self.assertEqual(15, date_util.num_years(begin))
        end = datetime.combine(date(2016, 06, 24), time(12, 30))
        self.assertEqual(16, date_util.num_years(begin, end), years)
