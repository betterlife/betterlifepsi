import unittest

from tests import fixture


class TestCases(unittest.TestCase):
    def setUp(self):
        self.app = fixture.init_app()

    def tearDown(self):
        fixture.cleanup_database(self.app.app_context())

    def test_get_next_code(self):
        from app.models import Supplier, User
        from app.utils import db_util
        user = User()
        user.organization_id = 1
        next_code = db_util.get_next_code(Supplier, user=user)
        self.assertEqual('000001', next_code)
