from flask import url_for
from flask_admin.babel import gettext

from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker


class TestPurchasePriceView(BaseTestCase):

    def test_purchase_order_hide_and_show(self):
        from app.service import Info
        from app.models.role import Role
        from app.utils import save_objects_commit
        role = Info.get_db().session.query(Role).filter_by(
            name='purchase_price_view').first()
        user, password = object_faker.user(
            ['product_view', 'direct_purchase_order_view']
        )
        save_objects_commit(user, role)
        fixture.login_user(self.test_client, user.email, password)

        rv = self.test_client.get('/admin/dpo/',
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

        rv = self.test_client.get('/admin/dpo/',
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
        from app.utils import save_objects_commit
        role = Info.get_db().session.query(Role).filter_by(
            name='purchase_price_view').first()
        user, password = object_faker.user(['product_view', 'direct_purchase_order_view'])
        user.roles.append(role)
        save_objects_commit(user, role)

        fixture.login_user(self.test_client, user.email, password)
        rv = self.test_client.get('/admin/dpo/',
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

        rv = self.test_client.get('/admin/dpo/',
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
        from app.utils import save_objects_commit
        def test_logic():
            fixture.login_as_admin(self.test_client)
            user, password = object_faker.user(role_names=[
                'purchase_price_view', 'direct_purchase_order_view', 'product_view'
            ])
            purchase_order = object_faker.purchase_order(number_of_line=1,
                                                         creator=user)
            save_objects_commit(purchase_order, user)
            po_url = url_for('dpo.details_view', id=purchase_order.id)
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
            role = Info.get_db().session.query(Role).filter_by(
                name='purchase_price_view'
            ).first()
            user.roles.remove(role)
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

        from tests.fixture import run_as_admin

        run_as_admin(self.test_client, test_logic)
