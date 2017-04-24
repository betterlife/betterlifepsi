from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker as of
from psi.app import const


class TestInventoryInOutLink(BaseTestCase):
    def test_enough_inventory(self):
        from psi.app.services.purchase_order import PurchaseOrderService
        with self.test_client:
            from tests.fixture import login_as_admin
            from psi.app.services import SalesOrderService
            from psi.app.models import EnumValues
            login_as_admin(self.test_client)
            po = of.purchase_order(number_of_line=2, type=EnumValues.get(const.DIRECT_PO_TYPE_KEY))
            products = [l.product for l in po.lines]
            receiving = PurchaseOrderService.create_receiving_if_not_exist(po)
            receiving.status = EnumValues.get(const.RECEIVING_COMPLETE_STATUS_KEY)
            in_trans_line = receiving.operate_inv_trans_by_recv_status()
            po = receiving.update_purchase_order_status()
            from psi.app.utils import db_util
            db_util.save_objects_commit(po, receiving, in_trans_line)
            so = of.sales_order(products=products, number_of_line=2)
            shipping = SalesOrderService.create_or_update_shipping(so)
            db_util.save_objects_commit(so, shipping)
            out_inv_trans = shipping.inventory_transaction
            self.assertIsNotNone(out_inv_trans)
            self.assertEquals(2,len(out_inv_trans.lines))
            for l in shipping.lines:
                self.assertEquals(1, len(l.inventory_links))
                link = l.inventory_links[0]
                self.assertIsNotNone(link)
                so_line = None
                for l in so.lines:
                    if l.product.id == link.product.id:
                        self.assertEquals(link.out_price, l.unit_price)
                        self.assertEquals(link.out_quantity, l.quantity)
                        so_line = l

                for recv_l in receiving.lines:
                    if recv_l.product.id == link.product.id:
                        self.assertEquals(link.in_price, recv_l.price)
                        in_trans_line = recv_l.inventory_transaction_line
                        remain_qty = recv_l.purchase_order_line.quantity - so_line.quantity
                        if remain_qty < 0:
                            self.assertEquals(0, in_trans_line.saleable_quantity)
                        else:
                            self.assertEquals(remain_qty, in_trans_line.saleable_quantity)
