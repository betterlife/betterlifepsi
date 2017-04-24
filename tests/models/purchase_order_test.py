import unittest

import psi.app.const as const
from psi.app.utils import db_util
from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker as of


class TestPurchaseOrder(BaseTestCase):

    def test_status_filter(self):
        from psi.app.models import PurchaseOrder

        def test_logic():
            po1, po2 = of.purchase_order(), of.purchase_order()
            from psi.app.models import EnumValues
            po1.status = EnumValues.get(const.PO_DRAFT_STATUS_KEY)
            po2.status = EnumValues.get(const.PO_ISSUED_STATUS_KEY)
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
        from psi.app.models import PurchaseOrder, EnumValues
        po_statuses = PurchaseOrder.status_option_filter().all()
        self.assertEquals(len(po_statuses), 6)
        self.assertIn(EnumValues.get(const.PO_ISSUED_STATUS_KEY), po_statuses)
        self.assertIn(EnumValues.get(const.PO_DRAFT_STATUS_KEY), po_statuses)
        self.assertIn(EnumValues.get(const.PO_REJECTED_STATUS_KEY), po_statuses)
        self.assertIn(EnumValues.get(const.PO_PART_RECEIVED_STATUS_KEY), po_statuses)
        self.assertIn(EnumValues.get(const.PO_RECEIVED_STATUS_KEY), po_statuses)
        self.assertIn(EnumValues.get(const.PO_SHIPPED_STATUS_KEY), po_statuses)

