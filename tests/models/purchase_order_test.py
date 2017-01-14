import unittest

import app.const as const
from app.utils import db_util
from tests import fixture
from tests.object_faker import object_faker as of


class TestPurchaseOrder(unittest.TestCase):
    def setUp(self):
        self.app = fixture.init_app()
        self.test_client = self.app.test_client()
        self.app_context = self.app.test_request_context()
        self.app_context.push()

    def tearDown(self):
        fixture.cleanup_database(self.app_context)
        self.app_context.pop()

    def test_status_filter(self):
        from app.models import PurchaseOrder

        def test_logic():
            po1, po2 = of.purchase_order(), of.purchase_order()
            from app.models import EnumValues
            po1.status = EnumValues.find_one_by_code(const.PO_DRAFT_STATUS_KEY)
            po2.status = EnumValues.find_one_by_code(const.PO_ISSUED_STATUS_KEY)
            db_util.save_objects_commit(po1, po2)
            po3 = PurchaseOrder.status_filter((const.PO_DRAFT_STATUS_KEY,)).all()[0]
            self.assertIsNotNone(po3)
            self.assertEqual(po1, po3)
            po4 = PurchaseOrder.status_filter((const.PO_ISSUED_STATUS_KEY,)).all()[0]
            self.assertIsNotNone(po4)
            self.assertEqual(po2, po4)

        from tests.fixture import run_as_admin
        run_as_admin(self.test_client, test_logic)

    def test_status_options(self):
        from app.models import PurchaseOrder, EnumValues
        po_statuses = PurchaseOrder.status_option_filter().all()
        self.assertEquals(len(po_statuses), 6)
        self.assertIn(EnumValues.find_one_by_code(const.PO_ISSUED_STATUS_KEY), po_statuses)
        self.assertIn(EnumValues.find_one_by_code(const.PO_DRAFT_STATUS_KEY), po_statuses)
        self.assertIn(EnumValues.find_one_by_code(const.PO_REJECTED_STATUS_KEY), po_statuses)
        self.assertIn(EnumValues.find_one_by_code(const.PO_PART_RECEIVED_STATUS_KEY), po_statuses)
        self.assertIn(EnumValues.find_one_by_code(const.PO_RECEIVED_STATUS_KEY), po_statuses)
        self.assertIn(EnumValues.find_one_by_code(const.PO_SHIPPED_STATUS_KEY), po_statuses)

