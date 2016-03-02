# coding=utf-8
import unittest
from datetime import datetime

import codecs
from app.models import SalesOrder, SalesOrderLine, Product, Supplier
from tests import fixture
from app.utils import db_util


class TestCases(unittest.TestCase):
    def setUp(self):
        self.test_client = fixture.get_test_client()
        fixture.login_as_admin(self.test_client)

    def test_import(self):
        content = codecs.open("tests/data/store_data.csv", "r", "utf-8").read()
        rv = self.test_client.get('/import_store_data')
        self.assertEqual(200, rv.status_code)
        self.assertIn(u'导入店铺运营数据', rv.data)
        rv = self.test_client.post('/import_store_data', data=dict(content=content), follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        self.assertEqual('Upload and import into system successfully', rv.data)

        self.assertIsNotNone(db_util.get_by_external_id(SalesOrder, '01201503130002'))

        self.assertIsNotNone(db_util.get_by_external_id(SalesOrderLine, '11'))
        self.assertIsNotNone(db_util.get_by_external_id(SalesOrderLine, '15'))
        self.assertIsNotNone(db_util.get_by_external_id(SalesOrderLine, '16'))
        self.assertIsNotNone(db_util.get_by_external_id(SalesOrderLine, '17'))
        self.assertIsNotNone(db_util.get_by_external_id(SalesOrderLine, '18'))

        self.assertIsNotNone(db_util.get_by_name(Product, '产品1'))
        self.assertIsNotNone(db_util.get_by_name(Product, '产品2'))
        self.assertIsNotNone(db_util.get_by_name(Product, '产品3'))
        self.assertIsNotNone(db_util.get_by_name(Product, '产品4'))
        self.assertIsNotNone(db_util.get_by_name(Product, '产品5'))

        self.assertEqual(3, SalesOrder.query.count())
        self.assertEqual(5, SalesOrderLine.query.count())
        self.assertEqual(5, Product.query.count())
        self.assertEqual(3, Supplier.query.count())

        sales_order = db_util.get_by_external_id(SalesOrder, '01201503130003')
        """:type: SalesOrder"""
        self.assertEqual(3, sales_order.lines.length)

        sales_order = db_util.get_by_external_id(SalesOrder, '01201503130001')
        self.assertEqual(1, sales_order.lines.length)
        line = sales_order.lines[0]
        """:type: SalesOrderLine"""
        self.assertEqual('15', line.external_id)
        self.assertEqual('产品2', line.product.name)
        self.assertEqual('000010', line.product.external_id)
        self.assertEquals('000016',line.product.supplier.external_id)
        self.assertEquals('供应商2',line.product.supplier.name)
        self.assertEquals(16.5000,line.product.purchase_price)
        self.assertEquals(33,line.product.retail_price)
        self.assertEqual(33, line.unit_price)
        self.assertEquals(1,line.quantity)
        self.assertEquals(datetime.strptime('2015-03-13 11:04:11.063', '%Y-%m-%d %H:%M:%S.%f'), line.sales_order.order_date)
        self.assertEqual(0, line.sales_order.logistic_amount)


