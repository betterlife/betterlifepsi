
import random

from flask import url_for
from six import iteritems

from tests import fixture
from psi.app import const
from psi.app.utils import db_util, calc_inline_field_name
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker as of


class TestSalesAmountAndProfitReportPage(BaseTestCase):

    def test_all_page_rendered(self):
        user, password = of.user(
            role_names=['report_view', ]
        )
        db_util.save_objects_commit(user)
        fixture.login_user(self.test_client, user.email, password)
        self.assertPageRendered(endpoint=url_for('sales_amount.index'))
        self.assertPageRendered(endpoint=url_for('sales_profit.index'))
        fixture.logout_user(self.test_client)
