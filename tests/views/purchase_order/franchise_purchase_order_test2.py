# coding=utf-8
import random

from flask import url_for

from psi.app import const
from psi.app.utils import db_util

from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.fixture import login_as_admin, login_user, run_as_admin
from tests.object_faker import object_faker
from psi.app.service import Info


class TestFranchisePurchaseOrderView2(BaseTestCase):

    def test_franchise_purchase_order_pages(self):
        from psi.app.models import EnumValues, Organization

        org_type = EnumValues.get(const.FRANCHISE_STORE_ORG_TYPE_KEY)
        organization = object_faker.organization(parent=Organization.query.get(1), type=org_type)
        user, pwd = object_faker.user(
            role_names=['franchise_purchase_order_create', 'franchise_purchase_order_edit',
                        'franchise_purchase_order_delete', 'franchise_purchase_order_view'],
            organization=organization)
        db_util.save_objects_commit(user, organization)
        login_user(self.test_client, user.email, pwd)
        self.assertPageRendered(url_for('fpo.index_view'))
        # self.assertPageRendered(url_for('fpo.create_view'))
        # draft_status = EnumValues.get(const.PO_DRAFT_STATUS_KEY)
        # order_date = object_faker.faker.date_time_this_year()
        # logistic_amount = random.randint(0, 100)
        # remark = object_faker.faker.text(max_nb_chars=50)

        # expect_contents = [draft_status.display, str(logistic_amount), order_date.strftime("%Y-%m-%d"), remark]
        # self.assertPageRendered(method=self.test_client.post,
        #                         data=dict(status=draft_status.id, order_date=order_date,
        #                                     logistic_amount=logistic_amount, remark=remark),
        #                         endpoint=self.create_endpoint(view='fpo'),
        #                         expect_contents=expect_contents)

        # self.assertPageRendered(expect_contents=expect_contents,
        #                         endpoint=url_for('fpo.edit_view', url=url_for('fpo.details_view', id=1), id=1))

        # new_remark = object_faker.faker.text(max_nb_chars=50)
        # new_logistic_amount = random.randint(0, 100)
        # new_order_date = object_faker.faker.date_time_this_year()
        # new_expect_contents = [draft_status.display, str(new_logistic_amount),
        #                         new_order_date.strftime("%Y-%m-%d"), new_remark]
        # self.assertPageRendered(method=self.test_client.post,
        #                         endpoint=self.edit_endpoint(view='fpo'),
        #                         data=dict(status=draft_status.id,
        #                                     order_date=new_order_date, logistic_amount=new_logistic_amount,
        #                                     remark=new_remark),
        #                         expect_contents=new_expect_contents)

        # rv = self.assertDeleteSuccessful(endpoint=url_for('fpo.delete_view'),
        #                                     deleted_data=[draft_status.display, new_remark,
        #                                                 new_order_date.strftime("%Y-%m-%d")],
        #                                     data=dict(url=url_for('fpo.index_view'), id='1'))
