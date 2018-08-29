from flask import url_for
from flask_admin.babel import gettext

from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker


class TestPurchasePriceView(BaseTestCase):

    def test_purchase_order_hide_then_show_list_page(self):
        from psi.app.service import Info
        from psi.app.models.role import Role
        from psi.app.utils import save_objects_commit
        role = Info.get_db().session.query(Role).filter_by(
            name='purchase_price_view').first()
        user, password = object_faker.user(
            ['product_view', 'direct_purchase_order_view']
        )
        save_objects_commit(user, role)
        fixture.login_user(self.test_client, user.email, password)

        rv = self.test_client.get(url_for('dpo.index_view'),
                                  follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertNotIn(b'<th class="column-header col-goods_amount">', rv.data,
                         b"goods amount should not exits in purchase order "
                         b"list page")
        self.assertNotIn(b'<th class="column-header col-total_amount">', rv.data,
                         b"total amount should not exits in purchase order "
                         b"list page")
        self.assertNotIn(b'<th class="column-header col-all_expenses">', rv.data,
                         b"all expenses should not exits in purchase order "
                         b"list page")
        rv = self.test_client.get(url_for('product.index_view'), follow_redirects=True)
        self.assertNotIn(b'<th class="column-header col-purchase_price">',
                         rv.data,
                         b"purchase price field should not exit in product "
                         b"list page")

        user.roles.append(role)
        save_objects_commit(user, role)

        rv = self.test_client.get(url_for('dpo.index_view'),
                                  follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'<th class="column-header col-goods_amount">', rv.data,
                      b"goods amount should exist in purchase order list page")
        self.assertIn(b'<th class="column-header col-total_amount">', rv.data,
                      b"total amount should exist in purchase order list page")
        self.assertIn(b'<th class="column-header col-all_expenses">', rv.data,
                      b"all expenses should exist in purchase order list page")
        rv = self.test_client.get(url_for('product.index_view'), follow_redirects=True)
        self.assertIn(b'<th class="column-header col-purchase_price">', rv.data,
                      b"purchase price field should exits in product list page")
        fixture.logout_user(self.test_client)

    def test_purchase_price_show_then_hidden_list_page(self):
        from psi.app.service import Info
        from psi.app.models.role import Role
        from psi.app.utils import save_objects_commit
        role = Info.get_db().session.query(Role).filter_by(
            name='purchase_price_view').first()
        user, password = object_faker.user(['product_view', 'direct_purchase_order_view'])
        user.roles.append(role)
        save_objects_commit(user, role)

        fixture.login_user(self.test_client, user.email, password)
        rv = self.test_client.get(url_for('dpo.index_view'),
                                  follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'<th class="column-header col-goods_amount">', rv.data,
                      b"goods amount not exits in purchase order list page")
        self.assertIn(b'<th class="column-header col-total_amount">', rv.data,
                      b"total amount not exits in purchase order list page")
        self.assertIn(b'<th class="column-header col-all_expenses">', rv.data,
                      b"all expenses not exits in purchase order list page")
        rv = self.test_client.get(url_for('product.index_view'), follow_redirects=True)
        self.assertIn(b'<th class="column-header col-purchase_price">', rv.data,
                      b"purchase price field should exits in product list page")

        user.roles.remove(role)
        save_objects_commit(user, role)

        rv = self.test_client.get(url_for('dpo.index_view'),
                                  follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertNotIn(b'<th class="column-header col-goods_amount">', rv.data,
                         b"goods amount should not exits in purchase order "
                         b"list page")
        self.assertNotIn(b'<th class="column-header col-total_amount">', rv.data,
                         b"total amount should not exits in purchase order "
                         b"list page")
        self.assertNotIn(b'<th class="column-header col-all_expenses">', rv.data,
                         b"all expenses should not exits in purchase order "
                         b"list page")
        rv = self.test_client.get(url_for('product.index_view'), follow_redirects=True)
        self.assertNotIn(b'<th class="column-header col-purchase_price">',
                         rv.data,
                         b"purchase price field should not exit in product "
                         b"list page")
        fixture.logout_user(self.test_client)

    def logic_for_detail_edit_page(self, user, password, po, po_url, product_url):
        from psi.app.service import Info
        from psi.app.models.role import Role
        from psi.app.utils import save_objects_commit
        fixture.login_as_admin(self.test_client)
        save_objects_commit(po, user)
        fixture.logout_user(self.test_client)
        fixture.login_user(self.test_client, user.email, password)
        rv = self.test_client.get(po_url, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        goods_amount_label = gettext('Goods Amount')
        self.assertIn(goods_amount_label.encode('utf-8'), rv.data)
        total_amount_label = gettext('Total Amount')
        self.assertIn(total_amount_label.encode('utf-8'), rv.data)

        rv = self.test_client.get(product_url, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        purchase_price_label = gettext('Purchase Price')
        self.assertIn(purchase_price_label.encode('utf-8'), rv.data)
        fixture.logout_user(self.test_client)
        role = Info.get_db().session.query(Role).filter_by(
            name='purchase_price_view'
        ).first()
        user.roles.remove(role)
        save_objects_commit(user)

        fixture.login_user(self.test_client, user.email, password)
        rv = self.test_client.get(po_url, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        goods_amount_label = gettext('Goods Amount')
        self.assertNotIn(goods_amount_label.encode('utf-8'), rv.data)
        total_amount_label = gettext('Total Amount')
        self.assertNotIn(total_amount_label.encode('utf-8'), rv.data)
        rv = self.test_client.get(product_url, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        purchase_price_label = gettext('Purchase Price')
        self.assertNotIn(purchase_price_label.encode('utf-8'), rv.data)
        fixture.logout_user(self.test_client)

    def test_purchase_price_show_and_hidden_detail_page(self):
        from tests.fixture import run_as_admin
        user, password = object_faker.user(role_names=[
            'purchase_price_view', 'direct_purchase_order_view', 'product_view'
        ])
        po = object_faker.purchase_order(number_of_line=1, creator=user)
        po_url = url_for('dpo.details_view', id=po.id)
        product_url = url_for('product.details_view', id=po.lines[0].product.id)
        run_as_admin(self.test_client, self.logic_for_detail_edit_page, user, password, po, po_url, product_url)

    def test_purchase_price_show_and_hidden_edit_page(self):
        user, password = object_faker.user(role_names=[
            'purchase_price_view', 'direct_purchase_order_view',
            'product_view', 'product_edit', 'direct_purchase_order_edit',
        ])
        po = object_faker.purchase_order(number_of_line=1, creator=user)
        po_url = url_for('dpo.edit_view', id=po.id)
        product_url = url_for('product.edit_view', id=po.lines[0].product.id)

        from tests.fixture import run_as_admin
        run_as_admin(self.test_client, self.logic_for_detail_edit_page, user, password, po, po_url, product_url)
