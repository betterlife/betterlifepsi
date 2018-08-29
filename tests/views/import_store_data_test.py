# coding=utf-8
from datetime import datetime

import codecs
from psi.app import const

from tests import fixture
from tests.base_test_case import BaseTestCase


class TestImportStoreDataView(BaseTestCase):

    def test_import(self):
        from psi.app.models import SalesOrder, SalesOrderLine, Product, Supplier
        from psi.app.utils import db_util
        import os
        fixture.login_as_admin(self.test_client)
        file_name = os.path.dirname(os.path.realpath(__file__)) + "/../resources/store_data.csv"
        content = codecs.open(file_name, "r", "utf-8").read()
        from psi.app.models.user import User
        from psi.app.models.role import Role
        from psi.app.service import Info
        user = Info.get_db().session.query(User).filter_by(login='super_admin').first()
        role = Info.get_db().session.query(Role).filter_by(name='import_store_data').first()
        user.roles.append(role)
        from psi.app.service import Info
        Info.get_db().session.add(user)
        Info.get_db().session.commit()
        rv = self.test_client.get('/admin/import_store_data/', follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        self.assertIn('导入店铺运营数据'.encode('utf-8'), rv.data)
        self.test_client.post('/admin/import_store_data/', data={
            'file': (file_name, content),
        }, follow_redirects=True)

        self.assertIsNotNone(db_util.get_by_external_id(SalesOrder, '01201503090002', user=user))

        self.assertIsNotNone(db_util.get_by_external_id(SalesOrderLine, '11', user=user))
        self.assertIsNotNone(db_util.get_by_external_id(SalesOrderLine, '15', user=user))
        self.assertIsNotNone(db_util.get_by_external_id(SalesOrderLine, '16', user=user))
        self.assertIsNotNone(db_util.get_by_external_id(SalesOrderLine, '17', user=user))
        self.assertIsNotNone(db_util.get_by_external_id(SalesOrderLine, '18', user=user))

        self.assertIsNotNone(db_util.get_by_name(Product, '产品1', user=user))
        self.assertIsNotNone(db_util.get_by_name(Product, '产品2', user=user))
        self.assertIsNotNone(db_util.get_by_name(Product, '产品3', user=user))
        self.assertIsNotNone(db_util.get_by_name(Product, '产品4', user=user))
        self.assertIsNotNone(db_util.get_by_name(Product, '产品5', user=user))

        self.assertEqual(3, SalesOrder.query.count())
        self.assertEqual(5, SalesOrderLine.query.count())
        self.assertEqual(5, Product.query.count())
        self.assertEqual(3, Supplier.query.count())

        sales_order = db_util.get_by_external_id(SalesOrder, '01201503130003', user=user)
        """:type: SalesOrder"""
        self.assertEqual(3, len(sales_order.lines))
        self.assertEqual(const.DIRECT_SO_TYPE_KEY, sales_order.type.code)

        sales_order = db_util.get_by_external_id(SalesOrder, '01201503130001', user=user)
        self.assertEqual(const.DIRECT_SO_TYPE_KEY, sales_order.type.code)
        self.assertEqual(user.organization_id, sales_order.organization_id)
        self.assertEqual(1, len(sales_order.lines))
        line = sales_order.lines[0]
        """:type: SalesOrderLine"""

        self.assertEqual('15', line.external_id)
        self.assertEqual('产品2', line.product.name)
        self.assertEquals(user.organization_id, line.product.organization_id)
        self.assertEqual('000010', line.product.external_id)
        self.assertEquals('000016', line.product.supplier.external_id)
        self.assertEquals('供应商2', line.product.supplier.name)
        self.assertEquals(user.organization_id, line.product.supplier.organization_id)
        self.assertEquals(16.5000, line.product.purchase_price)
        self.assertEquals(33, line.product.retail_price)
        self.assertEqual(33, line.unit_price)
        self.assertEquals(1, line.quantity)
        self.assertEquals(datetime.strptime('2015-03-13 11:04:11.063', '%Y-%m-%d %H:%M:%S.%f'), line.sales_order.order_date)
        self.assertEqual(0, line.sales_order.logistic_amount)
