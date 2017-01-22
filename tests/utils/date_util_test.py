# encoding=utf-8
import unittest
from datetime import datetime, date, time, timedelta

from app.utils import date_util


class TestDateUtil(unittest.TestCase):
    # TODO: Fix the issue that the result of testing depends on current date
    def test_num_years(self):
        begin = datetime.combine(date(2014, 6, 24), time(12, 30))
        years = date_util.num_years(begin)
        self.assertEqual(2, years)
        begin = datetime.combine(date(2000, 6, 24), time(12, 30))
        self.assertEqual(16, date_util.num_years(begin))
        end = datetime.combine(date(2016, 6, 24), time(12, 30))
        self.assertEqual(16, date_util.num_years(begin, end), years)
