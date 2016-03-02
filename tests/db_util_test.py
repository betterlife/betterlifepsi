import unittest

from tests import fixture


class TestCases(unittest.TestCase):
    def setUp(self):
        self.test_client = fixture.get_test_client()

    def test_get_next_code(self):
        from app.models.supplier import Supplier
        from app.utils import db_util
        next_code = db_util.get_next_code(Supplier)
        self.assertEqual('000001', next_code)
