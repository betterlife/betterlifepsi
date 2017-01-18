import unittest

from psi.app.utils import format_util


class TestFormatUtil(unittest.TestCase):
    def test_format_decimal(self):
        self.assertEqual('20.00', str(format_util.format_decimal(20.0005)))
        self.assertEqual('0.01', str(format_util.format_decimal(0.009)))
        self.assertEquals("2.25", str(format_util.format_decimal(2.249)))
        self.assertEquals("2.24", str(format_util.format_decimal(2.244)))
