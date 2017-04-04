# coding=utf-8
import random

from app import const
from app.utils import db_util

from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.fixture import login_as_admin, login_user, run_as_admin
from tests.object_faker import object_faker


class TestFranchisePurchaseOrderView(BaseTestCase):

    def test_to_organization_hide(self):

        from app.models import EnumValues, PurchaseOrder, Organization
        from app.service import Info
        from datetime import datetime
        t = EnumValues.get(const.FRANCHISE_STORE_ORG_TYPE_KEY)
        draft_status = EnumValues.get(const.PO_DRAFT_STATUS_KEY)
        draft_status_id = draft_status.id
        parent = Info.get_db().session.query(Organization).get(1)
        organization = object_faker.organization(type=t, parent=parent)
        user, password = object_faker.user(
            ['franchise_purchase_order_create', 'franchise_purchase_order_edit',
             'franchise_purchase_order_view', 'franchise_purchase_order_delete'],
            organization=organization
        )
        db_util.save_objects_commit(user)
        fixture.login_user(self.test_client, user.email, password)
        rv = self.test_client.get('/admin/fpo/new/', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertNotIn('to_organization', rv.data)

        remark = u'-备注信息-'
        order_date = '2016-08-25 23:18:55'
        rv = self.test_client.post('/admin/fpo/new/',
                                   follow_redirects=True,
                                   data=dict(status=draft_status_id,
                                             logistic_amount=20,
                                             order_date=order_date,
                                             _continue_editing=u'保存并继续编辑',
                                             remark=remark))
        self.assertEquals(rv.status_code, 200)

        po = PurchaseOrder.query.filter_by(remark=remark).first()
        self.assertIsNotNone(po)
        self.assertEquals(po.remark, remark)
        self.assertEquals(po.logistic_amount, 20)
        self.assertEquals(po.status.id, draft_status.id)
        self.assertEqual(po.order_date,
                         datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(po.to_organization, parent)
        self.assertEquals(po.organization, organization)

    def test_create_so_from_po(self):
        def test_login():
            from app.models import EnumValues
            f_type = EnumValues.get(const.FRANCHISE_PO_TYPE_KEY)
            po = object_faker.purchase_order(number_of_line=random.randint(1, 10), type=f_type)
            db_util.save_objects_commit(po)
            from app.views import FranchisePurchaseOrderAdmin
            sales_order, incoming, expense = FranchisePurchaseOrderAdmin.create_so_from_fpo(po)
            self.assertEquals(len(po.lines), len(sales_order.lines))
            self.assertEqual(sales_order.order_date, po.order_date)
            self.assertEquals(sales_order.type, EnumValues.get(const.FRANCHISE_SO_TYPE_KEY))
            self.assertEquals(sales_order.status, EnumValues.get(const.SO_CREATED_STATUS_KEY))
            self.assertEquals(sales_order.organization, po.to_organization)
            # There's no expense associated with the PO when creating PO for the franchise organization.
            # That's done on after_model_change in BasePurchaseOrderAdmin class
            self.assertEquals(sales_order.actual_amount, incoming.amount)
            self.assertIsNone(expense)

        run_as_admin(self.test_client, test_login)

    def test_not_allowed_if_not_franchise_organization(self):
        from app.models import EnumValues, Organization, PurchaseOrder
        with self.test_client:
            login_as_admin(self.test_client)
            org_type = EnumValues.get(const.DIRECT_SELLING_STORE_ORG_TYPE_KEY)
            organization = object_faker.organization(parent=Organization.query.get(1), type=org_type)
            user, pwd = object_faker.user(
                role_names=['franchise_purchase_order_create', 'franchise_purchase_order_edit',
                            'franchise_purchase_order_delete', 'franchise_purchase_order_view'],
                organization=organization)
            db_util.save_objects_commit(user, organization)
            login_user(self.test_client, user.email, pwd)
            draft_status = EnumValues.get(const.PO_DRAFT_STATUS_KEY)
            order_date = object_faker.faker.date_time_this_year()
            logistic_amount = random.randint(0, 100)
            remark = object_faker.faker.text(max_nb_chars=50)
            rv = self.test_client.post('/admin/fpo/new/?url=%2Fadmin%2Ffpo%2F',
                                       data=dict(status=draft_status.id, order_date=order_date,
                                                 logistic_amount=logistic_amount, remark=remark),
                                       follow_redirects=True)
            self.assertEqual(200, rv.status_code)
            self.assertIn('Your organization is not a franchise store and is not allowed to '
                          'create franchise purchase order', rv.data)
            po = PurchaseOrder.query.all()
            self.assertEqual(0, len(po))

    def test_franchise_purchase_order_pages(self):
        from app.models import EnumValues, Organization
        with self.test_client:
            login_as_admin(self.test_client)
            org_type = EnumValues.get(const.FRANCHISE_STORE_ORG_TYPE_KEY)
            organization = object_faker.organization(parent=Organization.query.get(1), type=org_type)
            user, pwd = object_faker.user(
                role_names=['franchise_purchase_order_create', 'franchise_purchase_order_edit',
                            'franchise_purchase_order_delete', 'franchise_purchase_order_view'],
                organization=organization)
            self.test_client.post('/login', data=dict(email_or_login=user.email,  password=pwd), follow_redirects=True)
            db_util.save_objects_commit(user, organization)
            login_user(self.test_client, user.email, pwd)
            self.assertPageRendered(endpoint='/admin/fpo/')
            self.assertPageRendered(endpoint='/admin/fpo/new/')
            draft_status = EnumValues.get(const.PO_DRAFT_STATUS_KEY)
            order_date = object_faker.faker.date_time_this_year()
            logistic_amount = random.randint(0, 100)
            remark = object_faker.faker.text(max_nb_chars=50)

            expect_contents = [draft_status.display, str(logistic_amount), order_date.strftime("%Y-%m-%d"), remark]
            self.assertPageRendered(method=self.test_client.post,
                                    data=dict(status=draft_status.id, order_date=order_date,
                                              logistic_amount=logistic_amount, remark=remark),
                                    endpoint='/admin/fpo/new/?url=%2Fadmin%2Ffpo%2F',
                                    expect_contents=expect_contents)

            self.assertPageRendered(expect_contents=expect_contents, endpoint='/admin/fpo/edit/?url=%2Fadmin%2Ffpo%2F&id=1')

            new_remark = object_faker.faker.text(max_nb_chars=50)
            new_logistic_amount = random.randint(0, 100)
            new_order_date = object_faker.faker.date_time_this_year()
            new_expect_contents = [draft_status.display, str(new_logistic_amount),
                                   new_order_date.strftime("%Y-%m-%d"), new_remark]
            self.assertPageRendered(method=self.test_client.post,
                                    endpoint='/admin/fpo/edit/?url=%2Fadmin%2Ffpo%2F&id=1',
                                    data=dict(status=draft_status.id,
                                              order_date=new_order_date, logistic_amount=new_logistic_amount,
                                              remark=new_remark),
                                    expect_contents=new_expect_contents)

            rv = self.assertDeleteSuccessful(endpoint='/admin/fpo/delete/',
                                             deleted_data=[draft_status.display, new_remark,
                                                           new_order_date.strftime("%Y-%m-%d")],
                                             data=dict(url='/admin/fpo/', id='1'))