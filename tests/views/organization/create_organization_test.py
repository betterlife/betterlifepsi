# coding=utf-8
from flask import url_for

from psi.app import const
from psi.app.utils import db_util
from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker
from tests.views.organization.base_organization_test import BaseOrganizationTestCase


class TestCreateOrganization(BaseOrganizationTestCase):

    def test_create(self):
        from psi.app.models import EnumValues
        type_id = EnumValues.get(const.DIRECT_SELLING_STORE_ORG_TYPE_KEY).id

        with self.test_client:
            fixture.login_as_admin(self.test_client)
            org_name = object_faker.faker.name()
            org_desc = object_faker.faker.text(max_nb_chars=20)
            create_url = self.create_endpoint(view='organization')
            self.assertPageRendered(
                endpoint=create_url,
                method=self.test_client.get,
                expect_contents=['betterlife', '直营店'])
            self.assertPageRendered(
                endpoint=create_url,
                method=self.test_client.post,
                expect_contents=[org_name, org_desc],
                data={
                    "type": type_id,
                    "name": org_name,
                    "description": org_desc,
                    "parent": 1
                })
            self.assertDeleteSuccessful(
                endpoint=url_for(
                    'organization.delete_view',
                    id=2,
                    url=url_for('organization.index_view')),
                deleted_data=[org_name, org_desc])

            from psi.app.models import Organization
            user, pwd = object_faker.user(
                role_names=[
                    'organization_create', 'organization_view',
                    'organization_delete', 'organization_edit'
                ],
                organization=Organization.query.get(1))
            db_util.save_objects_commit(user)
            fixture.login_user(self.test_client, user.email, pwd)
            from psi.app.models import EnumValues
            org_type = EnumValues.get(const.DIRECT_SELLING_STORE_ORG_TYPE_KEY)
            self.assertCreateFail(
                endpoint=create_url,
                create_data=[org_name, org_desc],
                data={
                    "type": org_type.id,
                    "name": org_name,
                    "description": org_desc,
                    "parent": 1
                })
