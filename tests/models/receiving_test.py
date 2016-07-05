from __future__ import print_function
import unittest
from datetime import datetime

from tests import fixture


class TestReceiving(unittest.TestCase):
    def setUp(self):
        self.app = fixture.init_app()
        self.test_client = self.app.test_client()
        self.app_context = self.app.test_request_context()
        self.app_context.push()

    def tearDown(self):
        fixture.cleanup_database(self.app_context)
        self.app_context.pop()

    def test_get_by_po_id(self):
        from app.models.receiving import Receiving
        from app.models.enum_values import EnumValues
        from app.database import DbInfo
        import app.const as const
        from tests.object_faker import object_faker

        def test_logic():
            po = object_faker.purchase_order()
            po.status = EnumValues.find_one_by_code(const.PO_RECEIVED_STATUS_KEY)
            receiving = Receiving()
            receiving.purchase_order = po
            receiving.date = datetime.now()
            receiving.status = EnumValues.find_one_by_code(const.RECEIVING_DRAFT_STATUS_KEY)
            db = DbInfo.get_db()

            db.session.add(po)
            db.session.add(receiving)
            receiving_returned = receiving.filter_by_po_id(1)[0]
            self.assertEqual(receiving, receiving_returned)

        from tests.fixture import run_test_as_admin
        run_test_as_admin(self.test_client, test_logic)

    def test_create_draft_recv_from_po(self):
        from app.models.receiving import Receiving
        from tests.object_faker import object_faker
        import app.const as const

        def test_logic():
            po = object_faker.purchase_order(number_of_line=2)
            receiving = Receiving.create_draft_recv_from_po(po)
            self.assertEquals(po, receiving.purchase_order)
            self.assertEquals(len(po.lines), len(receiving.lines))
            self.assertEquals(len(po.lines), len(receiving.inventory_transaction.lines))
            self.assertEquals(po.order_date, receiving.date)
            self.assertEquals(receiving.status.code, const.RECEIVING_DRAFT_STATUS_KEY)
            self.assertEquals(po.supplier,receiving.supplier)
            self.assertEquals(receiving.inventory_transaction.date,po.order_date)
            self.assertEquals(receiving.inventory_transaction.type.code, const.PURCHASE_IN_INV_TRANS_KEY)
            self.assertIsNotNone(receiving.inventory_transaction)

        from tests.fixture import run_test_as_admin
        run_test_as_admin(self.test_client, test_logic)