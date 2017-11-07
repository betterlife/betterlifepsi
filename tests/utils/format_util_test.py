# coding=utf-8
import unittest

from psi.app.utils import format_util


class TestFormatUtil(unittest.TestCase):

    def test_decimal_to_percent(self):
        self.assertEqual("33.33%", format_util.decimal_to_percent(0.3333))
        self.assertEqual("200.00%", format_util.decimal_to_percent(2))
        self.assertEqual("0.01%", format_util.decimal_to_percent(0.0001))

    def test_format_decimal(self):
        self.assertEqual('20.00', str(format_util.format_decimal(20.0005)))
        self.assertEqual('0.01', str(format_util.format_decimal(0.009)))
        self.assertEquals("2.25", str(format_util.format_decimal(2.249)))
        self.assertEquals("2.24", str(format_util.format_decimal(2.244)))

    def test_pinyin_first_letter(self):
        input = u'张三'
        self.assertEquals('zs', format_util.get_pinyin_first_letters(input))

    def test_pinyin_first_letter_multiple(self):
        input = u'朝小宇'
        self.assertEquals('cxy|zxy', format_util.get_pinyin_first_letters(input))

    def test_pinyin_last_letter_multiple(self):
        input = u'毛小调'
        self.assertEquals('mxd|mxt', format_util.get_pinyin_first_letters(input))

    def test_pinyin_middle_last_letter_multiple(self):
        input = u'毛朝调'
        self.assertEquals('mcd|mzd|mct|mzt', format_util.get_pinyin_first_letters(input))

    def get_pinyin_for_english(self):
        input = u'David Allen'
        self.assertEquals('David Allen', format_util.get_pinyin_first_letters(input))
