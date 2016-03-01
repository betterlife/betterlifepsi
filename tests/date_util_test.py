# encoding=utf-8
import unittest
from datetime import datetime, date, time

from app.utils import date_util


class TestCases(unittest.TestCase):
    def test_num_years(self):
        begin = datetime.combine(date(2014, 06, 24), time(12, 30))
        years = date_util.num_years(begin)
        self.assertEqual(1, years)
        begin = datetime.combine(date(2000, 06, 24), time(12, 30))
        self.assertEqual(15, date_util.num_years(begin))
        end = datetime.combine(date(2016, 06, 24), time(12,30))
        self.assertEqual(16, date_util.num_years(begin, end), years)