# coding=utf-8
from flask import url_for

from psi.app import const
from psi.app.utils import db_util
from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker
from tests.views.organization.base_organization_test import BaseOrganizationTestCase


class TestDeleteOrganization(BaseOrganizationTestCase):

    def test_delete_with_child_not_allowed(self):
        from psi.app.models import EnumValues, Organization
        type_id = EnumValues.get(const.DIRECT_SELLING_STORE_ORG_TYPE_KEY).id
        with self.test_client:
            fixture.login_as_admin(self.test_client)
            name1, desc1 = self.create_organization(
                type_id=type_id, parent_id=1)
            self.create_organization(type_id=type_id, parent_id=2)
            self.assertDeleteFail(
                endpoint=url_for(
                    'organization.delete_view',
                    id=2,
                    url=url_for('organization.index_view')),
                deleted_data=[name1, desc1])
            org = Organization.query.get(2)
            self.assertIsNotNone(org)
