import unittest

from tests import fixture


class TestPurchaseOrderView(unittest.TestCase):
    def setUp(self):
        self.app = fixture.init_app()
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        fixture.cleanup_database(self.app_context)
        self.app_context.pop()

    def create_user(self):
        from app.models.role import Role
        from app.service import Info
        from tests.object_faker import object_faker
        user, password = object_faker.user()
        role1 = Info.get_db().session.query(Role).filter_by(name='product_view').first()
        user.roles.append(role1)
        role2 = Info.get_db().session.query(Role).filter_by(name='purchase_order_view').first()
        user.roles.append(role2)
        return user, password

    def test_purchase_price_show_and_hidden(self):
        from app.service import Info
        from app.models.role import Role
        from app.utils.db_util import save_objects_commit
        role = Info.get_db().session.query(Role).filter_by(name='purchase_price_view').first()

        user1, password = self.create_user()
        user1.roles.append(role)
        save_objects_commit(user1)

        fixture.login_user(self.test_client, user1.email, password)
        rv = self.test_client.get('/admin/purchaseorder/', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn('<th class="column-header col-goods_amount">', rv.data,
                      "goods amount not exits in purchase order list page")
        self.assertIn('<th class="column-header col-total_amount">', rv.data,
                      "total amount not exits in purchase order list page")
        self.assertIn('<th class="column-header col-all_expenses">', rv.data,
                      "all expenses not exits in purchase order list page")
        rv = self.test_client.get('/admin/product/', follow_redirects=True)
        self.assertIn('<th class="column-header col-purchase_price">', rv.data,
                      "purchase price field should exits in product list page")
        user1.roles.remove(role)
        save_objects_commit(user1)
        rv = self.test_client.get('/admin/purchaseorder/', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertNotIn('<th class="column-header col-goods_amount">', rv.data,
                         "goods amount should not exits in purchase order list page")
        self.assertNotIn('<th class="column-header col-total_amount">', rv.data,
                         "total amount should not exits in purchase order list page")
        self.assertNotIn('<th class="column-header col-all_expenses">', rv.data,
                         "all expenses should not exits in purchase order list page")
        rv = self.test_client.get('/admin/product/', follow_redirects=True)
        self.assertNotIn('<th class="column-header col-purchase_price">', rv.data,
                         "purchase price field should not exit in product list page")

        user2, password = self.create_user()
        save_objects_commit(user2)
        fixture.login_user(self.test_client, user2.email, password)

        rv = self.test_client.get('/admin/purchaseorder/', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertNotIn('<th class="column-header col-goods_amount">', rv.data,
                         "goods amount should not exits in purchase order list page")
        self.assertNotIn('<th class="column-header col-total_amount">', rv.data,
                         "total amount should not exits in purchase order list page")
        self.assertNotIn('<th class="column-header col-all_expenses">', rv.data,
                         "all expenses should not exits in purchase order list page")
        rv = self.test_client.get('/admin/product/', follow_redirects=True)
        self.assertNotIn('<th class="column-header col-purchase_price">', rv.data,
                         "purchase price field should not exit in product list page")

        user1.roles.append(role)
        save_objects_commit(user2)

        fixture.login_user(self.test_client, user2.email, 'password')
        rv = self.test_client.get('/admin/purchaseorder/', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn('<th class="column-header col-goods_amount">', rv.data,
                      "goods amount should exist in purchase order list page")
        self.assertIn('<th class="column-header col-total_amount">', rv.data,
                      "total amount should exist in purchase order list page")
        self.assertIn('<th class="column-header col-all_expenses">', rv.data,
                      "all expenses should exist in purchase order list page")
        rv = self.test_client.get('/admin/product/', follow_redirects=True)
        self.assertIn('<th class="column-header col-purchase_price">', rv.data,
                      "purchase price field should exits in product list page")
