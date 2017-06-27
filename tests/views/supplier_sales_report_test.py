import random

from flask import url_for
from six import iteritems

from tests import fixture
from psi.app import const
from psi.app.utils import db_util, calc_inline_field_name
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker as of


class TestSupplierSalesReportPage(BaseTestCase):

    def test_all_page_rendered(self):
        user, password = of.user(
            role_names=['sales_report_view', ]
        )
        db_util.save_objects_commit(user)
        fixture.login_user(self.test_client, user.email, password)
        self.assertPageRendered(endpoint=url_for('supplier_sales_report.index_view', type='overall'))
        self.assertPageRendered(endpoint=url_for('supplier_sales_report.index_view', type='today'))
        self.assertPageRendered(endpoint=url_for('supplier_sales_report.index_view', type='yesterday'))
        self.assertPageRendered(endpoint=url_for('supplier_sales_report.index_view', type='this_week'))
        self.assertPageRendered(endpoint=url_for('supplier_sales_report.index_view', type='last_week'))
        self.assertPageRendered(endpoint=url_for('supplier_sales_report.index_view', type='this_month'))
        self.assertPageRendered(endpoint=url_for('supplier_sales_report.index_view', type='last_month'))
        self.assertPageRendered(endpoint=url_for('supplier_sales_report.index_view', type='this_quarter'))
        self.assertPageRendered(endpoint=url_for('supplier_sales_report.index_view', type='last_quarter'))
        self.assertPageRendered(endpoint=url_for('supplier_sales_report.index_view', type='this_year'))
        self.assertPageRendered(endpoint=url_for('supplier_sales_report.index_view', type='last_year'))
        fixture.logout_user(self.test_client)
