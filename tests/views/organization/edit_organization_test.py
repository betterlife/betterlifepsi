# coding=utf-8
from flask import url_for

from psi.app import const
from psi.app.utils import db_util
from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker
from tests.views.organization.base_organization_test import BaseOrganizationTestCase


class TestEditOrganization(BaseOrganizationTestCase):

    def test_edit(self):

        from psi.app.models import EnumValues
        type_id = EnumValues.get(const.DIRECT_SELLING_STORE_ORG_TYPE_KEY).id

        with self.test_client:
            fixture.login_as_admin(self.test_client)
            desc = object_faker.faker.text(max_nb_chars=20)
            name = object_faker.faker.name()
            self.assertPageRendered(
                endpoint=self.edit_endpoint(view='organization'),
                method=self.test_client.post,
                expect_contents=[name, desc],
                data={
                    "type": type_id,
                    "name": name,
                    "description": desc,
                    "parent": u'__None'
                })

            self.create_organization(type_id, parent_id=1)
            self.create_organization(type_id, parent_id=2)
            self.create_organization(type_id, parent_id=3)

            desc = object_faker.faker.text(max_nb_chars=20)
            name = object_faker.faker.name()
            self.assertPageRendered(
                endpoint=url_for(
                    'organization.edit_view',
                    id=4,
                    url=url_for('organization.index_view')),
                method=self.test_client.post,
                expect_contents=[name, desc],
                data={
                    "type": type_id,
                    "name": name,
                    "description": desc,
                    "parent": 1
                })
