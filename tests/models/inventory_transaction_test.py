from psi.app import const
from psi.app.service import Info
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker as of


class TestInventoryTransaction(BaseTestCase):
    def test_saleable_qty(self):
        from psi.app.services.purchase_order import PurchaseOrderService
        with self.test_client:
            from tests.fixture import login_as_admin
            login_as_admin(self.test_client)
            from psi.app.models import EnumValues
            db = Info.get_db()
            po = of.purchase_order(number_of_line=1, type=EnumValues.get(const.DIRECT_PO_TYPE_KEY))
            recv = PurchaseOrderService.create_receiving_if_not_exist(po)
            from psi.app.utils import db_util
            db_util.save_objects_commit(po, recv)
            recv.status = EnumValues.get(const.RECEIVING_COMPLETE_STATUS_KEY)
            inv_trans = recv.operate_inv_trans_by_recv_status()
            new_po = recv.update_purchase_order_status()
            db_util.save_objects_commit(new_po, inv_trans)
            self.assertEquals(inv_trans.lines[0].quantity, po.lines[0].quantity)
            self.assertEquals(inv_trans.lines[0].saleable_quantity, po.lines[0].quantity)
            self.assertEquals(inv_trans.lines[0].in_transit_quantity, 0)
            self.assertEqual(inv_trans.date, recv.date)
            self.assertEqual(inv_trans.lines[0].product, po.lines[0].product)
            self.assertEquals(inv_trans.lines[0].quantity, recv.lines[0].quantity)
            self.assertEquals(inv_trans.lines[0].saleable_quantity, recv.lines[0].quantity)
            self.assertEquals(inv_trans.lines[0].in_transit_quantity, 0)
            self.assertEqual(inv_trans.date, recv.date)
            self.assertEqual(inv_trans.lines[0].product, recv.lines[0].product)




