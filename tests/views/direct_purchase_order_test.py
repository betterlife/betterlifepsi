import random

from app import const
from app.utils import db_util
from tests.base_test_case import BaseTestCase
from tests.fixture import run_as_admin
from tests.object_faker import object_faker


class TestDirectPurchaseOrderPages(BaseTestCase):
    def test_direct_purchase_order_pages(self):
        from app.models import EnumValues

        def test_logic():
            supplier = object_faker.supplier()
            db_util.save_objects_commit(supplier)
            self.assertPageRendered(endpoint='/admin/dpo/')
            self.assertPageRendered(endpoint='/admin/dpo/new/')
            draft_status = EnumValues.find_one_by_code(const.PO_DRAFT_STATUS_KEY)
            order_date = object_faker.faker.date_time_this_year()
            logistic_amount = random.randint(0, 100)
            remark = object_faker.faker.text(max_nb_chars=50)

            expect_content = [supplier.name, draft_status.display, str(logistic_amount), order_date.strftime("%Y-%m-%d"), remark]
            self.assertPageRendered(method=self.test_client.post,
                                    data=dict(supplier=supplier.id, status=draft_status.id, order_date=order_date,
                                                   logistic_amount=logistic_amount, remark=remark),
                                    endpoint='/admin/dpo/new/?url=%2Fadmin%2Fdpo%2F',
                                    expect_contents=expect_content)

            self.assertPageRendered(expect_contents=expect_content, endpoint='/admin/dpo/edit/?url=%2Fadmin%2Fdpo%2F&id=1')

            new_remark = object_faker.faker.text(max_nb_chars=50)
            new_logistic_amount = random.randint(0, 100)
            new_order_date = object_faker.faker.date_time_this_year()
            new_expect_content = [supplier.name, draft_status.display, str(new_logistic_amount),
                                  new_order_date.strftime("%Y-%m-%d"), new_remark]
            self.assertPageRendered(method=self.test_client.post,
                                    endpoint='/admin/dpo/edit/?url=%2Fadmin%2Fdpo%2F&id=1',
                                    data=dict(supplier=supplier.id, status=draft_status.id,
                                                   order_date=new_order_date, logistic_amount=new_logistic_amount,
                                                   remark=new_remark),
                                    expect_contents=new_expect_content)

            rv = self.assertPageRendered(method=self.test_client.post,
                                         endpoint='/admin/dpo/delete/',
                                         data=dict(url='/admin/dpo/', id='1'))
            self.assertNotIn(supplier.name, rv.data)
            self.assertNotIn(draft_status.display, rv.data)
            self.assertNotIn(new_order_date.strftime("%Y-%m-%d"), rv.data)
            self.assertNotIn(new_remark, rv.data)

        run_as_admin(self.test_client, test_logic)
