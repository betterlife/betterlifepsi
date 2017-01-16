import unittest

import random

from app import const
from app.utils import db_util
from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.fixture import run_as_admin
from tests.object_faker import object_faker


class TestOpenAllPages(BaseTestCase):
    def setUp(self):
        self.app = fixture.init_app()
        self.test_client = self.app.test_client()
        self.app_context = self.app.test_request_context()
        self.app_context.push()

    def tearDown(self):
        fixture.cleanup_database(self.app_context)
        self.app_context.pop()

    def testOpenDashboard(self):

        def test_logic():
            rv = self.test_client.get('/admin')
            self.assertEqual(301, rv.status_code)
            rv = self.test_client.get('/admin/')
            self.assertAlmostEquals('utf-8', rv.charset)
            self.assertEqual(200, rv.status_code)

        run_as_admin(self.test_client, test_logic)

    def testOpenDirectPurchaseOrderPage(self):
        from app.models import EnumValues

        def test_logic():
            supplier = object_faker.supplier()
            db_util.save_objects_commit(supplier)
            self.assertPageRenderCorrect(endpoint='/admin/dpo/')
            self.assertPageRenderCorrect(endpoint='/admin/dpo/new/')
            draft_status = EnumValues.find_one_by_code(const.PO_DRAFT_STATUS_KEY)
            order_date = object_faker.faker.date_time_this_year()
            logistic_amount = random.randint(0, 100)
            remark = object_faker.faker.text(max_nb_chars=50)

            expect_content = [supplier.name, draft_status.display, str(logistic_amount), order_date.strftime("%Y-%m-%d"), remark]
            self.assertPageRenderCorrect(method=self.test_client.post,
                                         data=dict(supplier=supplier.id, status=draft_status.id, order_date=order_date,
                                                   logistic_amount=logistic_amount, remark=remark),
                                         endpoint='/admin/dpo/new/?url=%2Fadmin%2Fdpo%2F',
                                         expect_content=expect_content)

            self.assertPageRenderCorrect(expect_content=expect_content, endpoint='/admin/dpo/edit/?url=%2Fadmin%2Fdpo%2F&id=1')

            new_remark = object_faker.faker.text(max_nb_chars=50)
            new_logistic_amount = random.randint(0, 100)
            new_order_date = object_faker.faker.date_time_this_year()
            new_expect_content = [supplier.name, draft_status.display, str(new_logistic_amount),
                                  new_order_date.strftime("%Y-%m-%d"), new_remark]
            self.assertPageRenderCorrect(method=self.test_client.post,
                                         endpoint='/admin/dpo/edit/?url=%2Fadmin%2Fdpo%2F&id=1',
                                         data=dict(supplier=supplier.id, status=draft_status.id,
                                                   order_date=new_order_date, logistic_amount=new_logistic_amount,
                                                   remark=new_remark),
                                         expect_content=new_expect_content)

            rv = self.assertPageRenderCorrect(method=self.test_client.post,
                                              endpoint='/admin/dpo/delete/',
                                              data=dict(url='/admin/dpo/', id='1'))
            self.assertNotIn(supplier.name, rv.data)
            self.assertNotIn(draft_status.display, rv.data)
            self.assertNotIn(str(new_logistic_amount), rv.data)
            self.assertNotIn(new_order_date.strftime("%Y-%m-%d"), rv.data)
            self.assertNotIn(new_remark, rv.data)

        run_as_admin(self.test_client, test_logic)
