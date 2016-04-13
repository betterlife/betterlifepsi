# coding=utf-8
import unittest

from advice.inventory_advice import InventoryAdvice
from tests import fixture
from utils import get_next_code


class TestCases(unittest.TestCase):
    def setUp(self):
        self.app = fixture.init_app()
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        fixture.login_as_admin(self.test_client)
        from app.models import Product, User
        self.product = Product()
        self.product.organization_id = 1
        self.user = User()
        self.user.organization_id = 1
        self.product.code = get_next_code(Product, user=self.user)
        self.product.available_quantity = -1

    def tearDown(self):
        fixture.cleanup_database(self.app_context)
        self.app_context.pop()

    def test_no_available_qty(self):
        self.assertIn(u'-', InventoryAdvice.advice(self.product))
