import unittest, time

from flask import url_for
from flask.ext.admin.babel import gettext

from tests import fixture
from tests.object_faker import object_faker


class TestPurchasePriceView(unittest.TestCase):
    def setUp(self):
        self.app = fixture.init_app()
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()
        from app.service import Info
        Info.get_db().session.remove()
        Info.get_db().engine.execute('DROP TABLE alembic_version')
        Info.get_db().engine.execute('DROP VIEW sales_order_detail')
        Info.get_db().session.commit()
        Info.get_db().drop_all()

    def create_user(self):
        from app.models.role import Role
        from app.service import Info
        user, password = object_faker.user()
        role1 = Info.get_db().session.query(Role).filter_by(name='product_view').first()
        user.roles.append(role1)
        role2 = Info.get_db().session.query(Role).filter_by(name='purchase_order_view').first()
        user.roles.extend([role1, role2])
        return user, password

    def test_purchase_order_hide_and_show(self):
        from app.service import Info
        from app.models.role import Role
        from app.utils.db_util import save_objects_commit
        role = Info.get_db().session.query(Role).filter_by(
            name='purchase_price_view').first()
        user, password = self.create_user()
        save_objects_commit(user, role)
        fixture.login_user(self.test_client, user.email, password)

        rv = self.test_client.get('/admin/purchaseorder/',
                                  follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertNotIn('<th class="column-header col-goods_amount">', rv.data,
                         "goods amount should not exits in purchase order "
                         "list page")
        self.assertNotIn('<th class="column-header col-total_amount">', rv.data,
                         "total amount should not exits in purchase order "
                         "list page")
        self.assertNotIn('<th class="column-header col-all_expenses">', rv.data,
                         "all expenses should not exits in purchase order "
                         "list page")
        rv = self.test_client.get('/admin/product/', follow_redirects=True)
        self.assertNotIn('<th class="column-header col-purchase_price">',
                         rv.data,
                         "purchase price field should not exit in product "
                         "list page")

        user.roles.append(role)
        save_objects_commit(user, role)

        rv = self.test_client.get('/admin/purchaseorder/',
                                  follow_redirects=True)
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
        fixture.logout_user(self.test_client)

    def test_purchase_price_show_and_hidden(self):
        from app.service import Info
        from app.models.role import Role
        from app.utils.db_util import save_objects_commit
        role = Info.get_db().session.query(Role).filter_by(
            name='purchase_price_view').first()
        user, password = self.create_user()
        user.roles.append(role)
        save_objects_commit(user, role)

        fixture.login_user(self.test_client, user.email, password)
        rv = self.test_client.get('/admin/purchaseorder/',
                                  follow_redirects=True)
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

        user.roles.remove(role)
        save_objects_commit(user, role)

        rv = self.test_client.get('/admin/purchaseorder/',
                                  follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertNotIn('<th class="column-header col-goods_amount">', rv.data,
                         "goods amount should not exits in purchase order "
                         "list page")
        self.assertNotIn('<th class="column-header col-total_amount">', rv.data,
                         "total amount should not exits in purchase order "
                         "list page")
        self.assertNotIn('<th class="column-header col-all_expenses">', rv.data,
                         "all expenses should not exits in purchase order "
                         "list page")
        rv = self.test_client.get('/admin/product/', follow_redirects=True)
        self.assertNotIn('<th class="column-header col-purchase_price">',
                         rv.data,
                         "purchase price field should not exit in product "
                         "list page")
        fixture.logout_user(self.test_client)

    def test_purchase_price_show_and_hidden_detail_page(self):
        from app.service import Info
        from app.models.role import Role
        from app.utils.db_util import save_objects_commit
        with self.test_client:
            fixture.login_as_admin(self.test_client)
            user, password = object_faker.user()
            purchase_order = object_faker.purchase_order(number_of_line=1,
                                                         creator=user)
            role1 = Info.get_db().session.query(Role).filter_by(
                name='purchase_price_view'
            ).first()
            role2 = Info.get_db().session.query(Role).filter_by(
                name='purchase_order_view'
            ).first()
            role3 = Info.get_db().session.query(Role).filter_by(
                name='product_view'
            ).first()
            user.roles.extend([role1, role2, role3])
            save_objects_commit(purchase_order, user)
            po_url = url_for('purchaseorder.details_view', id=purchase_order.id)
            product_url = url_for('product.details_view',
                                  id=purchase_order.lines[0].product.id)
            fixture.logout_user(self.test_client)
            fixture.login_user(self.test_client, user.email, password)
            rv = self.test_client.get(po_url)
            self.assertEqual(rv.status_code, 200)
            goods_amount_label = gettext('Goods Amount')
            self.assertIn(goods_amount_label, rv.data)
            total_amount_label = gettext('Total Amount')
            self.assertIn(total_amount_label, rv.data)

            rv = self.test_client.get(product_url)
            self.assertEqual(rv.status_code, 200)
            purchase_price_label = gettext('Purchase Price')
            self.assertIn(purchase_price_label, rv.data)
            fixture.logout_user(self.test_client)

            user.roles.remove(role1)
            save_objects_commit(user)

            fixture.login_user(self.test_client, user.email, password)
            rv = self.test_client.get(po_url)
            self.assertEqual(rv.status_code, 200)
            goods_amount_label = gettext('Goods Amount')
            self.assertNotIn(goods_amount_label, rv.data)
            total_amount_label = gettext('Total Amount')
            self.assertNotIn(total_amount_label, rv.data)
            rv = self.test_client.get(product_url)
            self.assertEqual(rv.status_code, 200)
            purchase_price_label = gettext('Purchase Price')
            self.assertNotIn(purchase_price_label, rv.data)
            fixture.logout_user(self.test_client)

