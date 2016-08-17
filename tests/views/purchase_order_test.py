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

    def create_test_user(self):
        from app.models.user import User
        from app.models.role import Role
        from flask_security.utils import encrypt_password
        from app.service import Info
        user = User()
        email = "ppu@betterlife.io"
        password = 'password'
        user.email = email
        user.active = True
        user.login = "purchase_price_view_user"
        user.display = "Purchase price view user"
        user.password = encrypt_password(password)
        role2 = Info.get_db().session.query(Role).filter_by(name='purchase_order_view').first()
        user.roles.append(role2)
        return user

    def purchase_price_view(self):
        from app.service import Info
        from app.models.role import Role
        from app.utils.db_util import save_objects_commit
        # Create a user
        user = self.create_test_user()
        # Assign the purchase_price_view and purchase_order_view role to the user
        role = Info.get_db().session.query(Role).filter_by(name='purchase_price_view').first()
        user.roles.append(role)
        # Visit the purchase order list page
        save_objects_commit(user)
        # Make sure user can see the total amount, goods amount and
        fixture.login_user(self.test_client, user.email, 'password')
        rv = self.test_client.get('/admin/purchaseorder/',
                                  follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn('<th class="column-header col-goods_amount">', rv.data,
                      "goods amount not exits in purchase order list page")
        self.assertIn('<th class="column-header col-total_amount">', rv.data,
                      "total amount not exits in purchase order list page")
        self.assertIn('<th class="column-header col-all_expenses">', rv.data,
                      "all expenses not exits in purchase order list page")

    def purchase_price_hidden_then_show(self):
        from app.service import Info
        from app.models.role import Role
        from app.utils.db_util import save_objects_commit
        # Create a user
        user = self.create_test_user()
        save_objects_commit(user)
        # Make sure user can see the total amount, goods amount and
        fixture.login_user(self.test_client, user.email, 'password')
        rv = self.test_client.get('/admin/purchaseorder/',
                                  follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        # Check field should be hidden
        self.assertNotIn('<th class="column-header col-goods_amount">', rv.data,
                         "goods amount should not exits in purchase order list page")
        self.assertNotIn('<th class="column-header col-total_amount">', rv.data,
                         "total amount should not exits in purchase order list page")
        self.assertNotIn('<th class="column-header col-all_expenses">', rv.data,
                         "all expenses should not exits in purchase order list page")
        # Add purchase_price_view role to user
        role = Info.get_db().session.query(Role).filter_by(name='purchase_price_view').first()
        user.roles.append(role)
        # Visit the purchase order list page
        save_objects_commit(user)
        # Make sure user can see the total amount, goods amount and
        fixture.login_user(self.test_client, user.email, 'password')
        rv = self.test_client.get('/admin/purchaseorder/',
                                  follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn('<th class="column-header col-goods_amount">', rv.data,
                      "goods amount should exist in purchase order list page")
        self.assertIn('<th class="column-header col-total_amount">', rv.data,
                      "total amount should exist in purchase order list page")
        self.assertIn('<th class="column-header col-all_expenses">', rv.data,
                      "all expenses should exist in purchase order list page")
