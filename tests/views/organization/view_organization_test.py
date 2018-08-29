# coding=utf-8
from flask import url_for

from psi.app import const
from psi.app.utils import db_util
from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker
from tests.views.organization.base_organization_test import BaseOrganizationTestCase


class TestViewOrganization(BaseOrganizationTestCase):

    def test_view(self):
        with self.test_client:
            fixture.login_as_admin(self.test_client)
            self.assertPageRendered(
                endpoint=url_for('organization.index_view'),
                method=self.test_client.get,
                expect_contents=['betterlife', '1', u'直营店'])

