# coding=utf-8
from datetime import datetime, timedelta

from psi.app.const import *

from psi.app.advice import InventoryAdvice
from tests import fixture
from tests.base_test_case import BaseTestCase


class TestInventoryAdvice(BaseTestCase):
    def setUp(self):
        super(TestInventoryAdvice, self).setUp()
        from psi.app.utils import get_next_code
        fixture.login_as_admin(self.test_client)
        from psi.app.models import Product, User, ProductInventory
        self.product = ProductInventory()
        self.product.organization_id = 1
        self.user = User()
        self.user.organization_id = 1
        self.product.code = get_next_code(Product, user=self.user)
        self.product.id = 1

    def tearDown(self):
        super(TestInventoryAdvice, self).tearDown()

    def test_no_available_qty(self):
        self.assertIn(u'-', InventoryAdvice.advice(self.product))

    def test_negative_qty(self):
        TestInventoryAdvice.adjust_product_quantity(self.product, date=datetime.now(), quantity=-1,
                                                    price=1, type_code=SALES_OUT_INV_TRANS_TYPE_KEY)
        self.assertIn("库存错误", InventoryAdvice.advice(self.product))

    @staticmethod
    def adjust_product_quantity(product, date, quantity, price, type_code):
        from psi.app.models import InventoryTransactionLine, InventoryTransaction, EnumValues
        it = InventoryTransaction()
        it.date = date
        it.type = EnumValues.get(type_code)
        itl = InventoryTransactionLine()
        itl.quantity = quantity
        itl.product_id = product.id
        itl.inventory_transaction = it
        itl.price = price
        if product.inventory_transaction_lines is None:
            product.inventory_transaction_lines = [itl]
        else:
            product.inventory_transaction_lines.append(itl)

    def test_zero_qty(self):
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=14), 20, 20, PURCHASE_IN_INV_TRANS_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=14), -2, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=5), -3, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=5), -8, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.now(), -7, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        self.product.lead_day = 2
        self.product.deliver_day = 3
        advice = InventoryAdvice.advice(self.product)
        self.assertIn("请立即补货", advice)
        self.assertIn('补货需要<span class="i_a_warning i_a_number">5.00</span>天', advice)
        self.assertIn('补货期间损失利润:<span class="i_a_warning i_a_number">71.43</span>元', advice)

    def test_enough_qty(self):
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=14), 40, 20, PURCHASE_IN_INV_TRANS_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=14), -5, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=5), -3, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=4), -8, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=3), -8, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.now(), -4, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        self.product.lead_day = 2
        self.product.deliver_day = 3
        advice = InventoryAdvice.advice(self.product)
        self.assertIn('当前库存可供销售<span class="i_a_number">6.00</span>天', advice)

    def test_not_enough_qty(self):
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=14), 35, 20, PURCHASE_IN_INV_TRANS_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=14), -5, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=5), -3, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=4), -8, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.today() - timedelta(days=3), -8, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        TestInventoryAdvice.adjust_product_quantity(self.product, datetime.now(), -4, 30, SALES_OUT_INV_TRANS_TYPE_KEY)
        self.product.lead_day = 2
        self.product.deliver_day = 3
        advice = InventoryAdvice.advice(self.product)
        self.assertIn('当前库存在新货品到达前即会售完', advice)
        self.assertIn('可销售<span class="i_a_number">3.50</span>天', advice)
        self.assertIn('补货需要<span class="i_a_number">5.00</span>天', advice)
        self.assertIn('补货期间损失利润额<span class="i_a_number i_a_warning">30.00</span>元', advice)
        self.assertIn('<a href="/admin/dpo/new/" target="_blank">点此补货</a>', advice)