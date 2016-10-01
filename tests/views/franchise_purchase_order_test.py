# coding=utf-8
import unittest

from flask import url_for

from app import const
from tests import fixture
from tests.object_faker import object_faker
from app.utils import db_util


class TestFranchisePurchaseOrderView(unittest.TestCase):
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
        Info.get_db().reflect()
        Info.get_db().drop_all()

    def test_to_organization_hide(self):

        from app.models import EnumValues, PurchaseOrder, Organization
        from app.service import Info
        from datetime import datetime
        t = EnumValues.find_one_by_code(u"FRANCHISE_STORE")
        draft_status = EnumValues.find_one_by_code(const.PO_DRAFT_STATUS_KEY)
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
        print (rv.data)
        self.assertEquals(rv.status_code,200)

        po = PurchaseOrder.query.filter_by(remark=remark).first()
        self.assertIsNotNone(po)
        self.assertEquals(po.remark,remark)
        self.assertEquals(po.logistic_amount,20)
        self.assertEquals(po.status.id, draft_status.id)
        self.assertEqual(po.order_date,
                         datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(po.to_organization, parent)
        self.assertEquals(po.organization, organization)

