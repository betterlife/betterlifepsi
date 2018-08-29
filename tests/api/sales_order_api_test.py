import unittest

from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker
from psi.app.utils import db_util
from psi.app.const import SO_DELIVERED_STATUS_KEY, SO_SHIPPED_STATUS_KEY, FRANCHISE_SO_TYPE_KEY
from tests.fixture import run_as_admin
from psi.app.service import Info


class TestSalesOrderApi(BaseTestCase):

    def test_update_sales_order_complete_status_success(self):
        from psi.app.models import EnumValues, SalesOrder

        def test_logic():
            fixture.login_as_admin(self.test_client)
            user, password = object_faker.user(role_names=[
                'franchise_sales_order_create',
                'franchise_sales_order_view',
                'franchise_sales_order_edit',
                'product_view'
            ])
            franchise_so_type = EnumValues.get(FRANCHISE_SO_TYPE_KEY)
            sales_order = object_faker.sales_order(creator=user,
                                                   number_of_line=1,
                                                   type=franchise_so_type)
            db_util.save_objects_commit(sales_order, user)
            so_id = sales_order.id
            delivered_status = EnumValues.get(SO_DELIVERED_STATUS_KEY)
            fixture.login_user(self.test_client, user.email, password)
            rv = self.test_client.put('/api/sales_order/' + str(so_id),
                                      follow_redirects=True,
                                      data=dict(status_id=delivered_status.id))
            self.assertIn(b'message', rv.data)
            self.assertIn(b'Status update successfully', rv.data)
            self.assertEqual(rv.status_code, 200)
            so_from_db = Info.get_db().session.query(SalesOrder).get(so_id)
            self.assertIsNotNone(so_from_db)
            self.assertEquals(SO_DELIVERED_STATUS_KEY, so_from_db.status.code)
        run_as_admin(self.test_client, test_logic)

    def test_update_sales_order_shipped_status_success(self):
        from psi.app.models import EnumValues, SalesOrder

        def test_logic():
            fixture.login_as_admin(self.test_client)
            user, password = object_faker.user(role_names=[
                'franchise_sales_order_create',
                'franchise_sales_order_view',
                'franchise_sales_order_edit',
                'product_view'
            ])
            franchise_so_type = EnumValues.get(FRANCHISE_SO_TYPE_KEY)
            sales_order = object_faker.sales_order(creator=user,
                                                   number_of_line=1,
                                                   type=franchise_so_type)
            db_util.save_objects_commit(sales_order, user)
            so_id = sales_order.id
            shipped_status = EnumValues.get(SO_SHIPPED_STATUS_KEY)
            fixture.login_user(self.test_client, user.email, password)
            rv = self.test_client.put('/api/sales_order/' + str(so_id),
                                      follow_redirects=True,
                                      data=dict(status_id=shipped_status.id))
            self.assertIn(b'message', rv.data)
            self.assertIn(b'Status update successfully', rv.data)
            self.assertEqual(rv.status_code, 200)
            so_from_db = Info.get_db().session.query(SalesOrder).get(so_id)
            self.assertIsNotNone(so_from_db)
            self.assertEquals(SO_SHIPPED_STATUS_KEY, so_from_db.status.code)
        run_as_admin(self.test_client, test_logic)

    def test_update_sales_order_unauthorized(self):
        from psi.app.models import EnumValues, SalesOrder

        def test_logic():
            fixture.login_as_admin(self.test_client)
            user, password = object_faker.user(role_names=[
                'franchise_sales_order_create',
                'franchise_sales_order_view',
                'product_view'
            ])
            sales_order = object_faker.sales_order(creator=user,
                                                   number_of_line=1)
            db_util.save_objects_commit(sales_order, user)
            so_id = sales_order.id
            delivered_status = EnumValues.get(SO_DELIVERED_STATUS_KEY)
            fixture.logout_user(self.test_client)
            rv = self.test_client.put('/api/sales_order/' + str(so_id),
                                      follow_redirects=True,
                                      data=dict(status_id=delivered_status.id))
            self.assertEqual(rv.status_code, 403)
        run_as_admin(self.test_client, test_logic)

    def test_update_sales_order_has_no_role(self):
        from psi.app.models import EnumValues

        def test_logic():
            fixture.login_as_admin(self.test_client)
            user, password = object_faker.user(role_names=[
                'franchise_sales_order_create',
                'franchise_sales_order_view',
                'product_view'
            ])
            sales_order = object_faker.sales_order(creator=user,
                                                   number_of_line=1)
            db_util.save_objects_commit(sales_order, user)
            so_id = sales_order.id
            delivered_status = EnumValues.get(SO_DELIVERED_STATUS_KEY)
            fixture.login_user(self.test_client, user.email, password)
            rv = self.test_client.put('/api/sales_order/' + str(so_id),
                                      follow_redirects=True,
                                      data=dict(status_id=delivered_status.id))
            self.assertEqual(rv.status_code, 403)
        run_as_admin(self.test_client, test_logic)

    def test_update_sales_order_status_invalid(self):
        def test_logic():
            fixture.login_as_admin(self.test_client)
            user, password = object_faker.user(role_names=[
                'franchise_sales_order_create',
                'franchise_sales_order_view',
                'franchise_sales_order_edit',
                'product_view'
            ])
            sales_order = object_faker.sales_order(creator=user,
                                                   number_of_line=1)
            db_util.save_objects_commit(sales_order, user)
            so_id = sales_order.id
            fixture.login_user(self.test_client, user.email, password)
            rv = self.test_client.put('/api/sales_order/' + str(so_id),
                                      follow_redirects=True,
                                      data=dict(status_id=5000))
            self.assertEqual(rv.status_code, 201)
            self.assertIn(b'message', rv.data)
            self.assertIn(b'Invalid sales order status parameter', rv.data)
        run_as_admin(self.test_client, test_logic)

    def test_update_sales_order_status_not_allowed(self):
        from psi.app.models import EnumValues

        def test_logic():
            fixture.login_as_admin(self.test_client)
            user, password = object_faker.user(role_names=[
                'franchise_sales_order_create',
                'franchise_sales_order_view',
                'franchise_sales_order_edit',
                'product_view'
            ])
            sales_order = object_faker.sales_order(creator=user,
                                                   number_of_line=1)
            shipped_status = EnumValues.get(SO_SHIPPED_STATUS_KEY)
            sales_order.status = shipped_status
            db_util.save_objects_commit(sales_order, user)
            so_id = sales_order.id
            fixture.login_user(self.test_client, user.email, password)
            rv = self.test_client.put('/api/sales_order/' + str(so_id),
                                      follow_redirects=True,
                                      data=dict(status_id=shipped_status.id))
            self.assertEqual(rv.status_code, 201)
            self.assertIn(b'message', rv.data)
            self.assertIn(b'Status update not allowed', rv.data)
        run_as_admin(self.test_client, test_logic)
