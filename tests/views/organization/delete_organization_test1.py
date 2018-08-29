# coding=utf-8
from flask import url_for

from psi.app import const
from psi.app.utils import db_util
from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker
from tests.views.organization.base_organization_test import BaseOrganizationTestCase


class TestDeleteOrganization(BaseOrganizationTestCase):

    def test_delete_root_not_allowed(self):
        from psi.app.models import EnumValues
        type_id = EnumValues.get(const.DIRECT_SELLING_STORE_ORG_TYPE_KEY).id

        with self.test_client:
            fixture.login_as_admin(self.test_client)
            name = object_faker.faker.name()
            desc = object_faker.faker.text(max_nb_chars=20)
            self.assertPageRendered(
                endpoint=url_for(
                    'organization.edit_view',
                    id=1,
                    url=url_for('organization.index_view')),
                method=self.test_client.post,
                expect_contents=[name, desc],
                data={
                    "type": type_id,
                    "name": name,
                    "description": desc,
                    "parent": u'__None'
                })
            self.assertPageRendered(
                endpoint=url_for(
                    'organization.delete_view',
                    url=url_for('organization.index_view'),
                    id=1),
                method=self.test_client.post,
                expect_contents=[name, desc, "1"],
                data={
                    "type": type_id,
                    "name": name,
                    "description": desc,
                    "parent": u'__None'
                })

