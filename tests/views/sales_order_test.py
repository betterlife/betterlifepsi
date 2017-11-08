import random

from flask import url_for
from six import iteritems

from tests import fixture
from psi.app import const
from psi.app.utils import db_util, calc_inline_field_name
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker as of


class TestSalesOrderPages(BaseTestCase):
    def test_sales_order_list_create_page(self):
        user, password = of.user(
            role_names=['direct_sales_order_create', 'direct_sales_order_view']
        )
        db_util.save_objects_commit(user)
        fixture.login_user(self.test_client, user.email, password)
        self.assertPageRendered(endpoint=url_for('salesorder.index_view'))
        self.assertPageRendered(endpoint=url_for('salesorder.create_view'))
        fixture.logout_user(self.test_client)

        # The follow test case will fail according to bug BE-325
        # user, password = of.user(
        #     role_names = ['franchise_sales_order_create', 'franchise_sales_order_view']
        # )
        # db_util.save_objects_commit(user)
        # fixture.login_user(self.test_client, user.email, password)
        # self.assertPageRendered(endpoint=url_for('salesorder.index_view'))
        # self.assertPageRendered(endpoint=url_for('salesorder.create_view'))

    def test_update_sales_order(self):
        data, expect = self.create_sales_order(status_key=const.SO_CREATED_STATUS_KEY)
        customer, delivered, total = expect[0], expect[1], float(expect[4])
        self.assertPageRendered(expect_contents=expect,
                                endpoint=self.edit_endpoint(view='salesorder'))

        new_remark = of.faker.text(max_nb_chars=50)
        new_logistic_amount = random.randint(0, 100)
        new_order_date = of.faker.date_time_this_year()
        new_expect = [customer, delivered, str(new_logistic_amount), str(total),
                      new_order_date.strftime("%Y-%m-%d"), new_remark]
        data['logistic_amount'] = new_logistic_amount
        data['order_date'] = new_order_date
        data['remark'] = new_remark
        new_data = dict()
        for k,v in iteritems(data):
            if k.startswith('lines-') is False:
                new_data[k] = v
        self.assertPageRendered(method=self.test_client.post,
                                endpoint=url_for('salesorder.edit_view',
                                                 url=url_for(
                                                     'salesorder.index_view'),
                                                 id=1),
                                data=data, expect_contents=new_expect)

    def test_delete_sales_order(self):
        data, expect = self.create_sales_order(status_key=const.SO_CREATED_STATUS_KEY)
        self.assertDeleteSuccessful(endpoint=url_for('salesorder.delete_view',
                                                     id= 1,
                                                     url=url_for('salesorder.index_view')),
                                    deleted_data=expect)

    def test_create_sales_order(self):
        self.create_sales_order(status_key=const.SO_DELIVERED_STATUS_KEY)

    def create_sales_order(self, status_key):
        from psi.app.models import EnumValues
        from psi.app.services.purchase_order import PurchaseOrderService
        user, password = of.user(
            role_names=['direct_sales_order_create',
                        'direct_sales_order_view',
                        'direct_sales_order_edit',
                        'direct_sales_order_delete']
        )
        db_util.save_objects_commit(user)
        fixture.login_as_admin(self.test_client)
        fixture.login_user(self.test_client, user.email, password)
        direct_po = EnumValues.get(const.DIRECT_PO_TYPE_KEY)
        po = of.purchase_order(number_of_line=2, type=direct_po,
                               creator=user)
        po.status = EnumValues.get(const.PO_ISSUED_STATUS_KEY)
        fixture.login_as_admin(self.test_client)
        l_e, g_e, recv = PurchaseOrderService.create_expense_receiving(po)
        customer = of.customer(creator=user)
        db_util.save_objects_commit(po, l_e, g_e, recv, customer)
        fixture.logout_user(self.test_client)
        fixture.login_user(self.test_client, user.email, password)
        order_status = EnumValues.get(status_key)
        order_date = of.faker.date_time_this_year()
        logistic_amount = random.randint(0, 100)
        remark = of.faker.text(max_nb_chars=50)
        data = dict(customer=customer.id, status=order_status.id,
                    order_date=order_date, logistic_amount=logistic_amount,
                    remark=remark)
        total, data = self.prepare_so_lines_data_from_po(po, data)
        expect = [customer.name, order_status.display,
                  order_date.strftime("%Y-%m-%d"), remark, str(total)]
        self.assertPageRendered(method=self.test_client.post, data=data,
                                endpoint=self.create_endpoint(view='salesorder'),
                                expect_contents=expect)
        return data, expect

    def prepare_so_lines_data_from_po(self, po, data):
        total = 0
        po_lines = po.lines
        for i in range(2):
            data[calc_inline_field_name(i, 'id')] = i + 1
            data[calc_inline_field_name(i, 'product')] = po_lines[
                i].product.id
            data[calc_inline_field_name(i, 'unit_price')] = po_lines[
                i].product.retail_price
            data[calc_inline_field_name(i, 'quantity')] = random.randint(1,
                                                                         20)
            total += data[calc_inline_field_name(i, 'unit_price')] * data[
                calc_inline_field_name(i, 'quantity')]
        return total, data
