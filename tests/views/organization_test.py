# coding=utf-8
from flask import url_for

from psi.app import const
from psi.app.utils import db_util
from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker


class TestOrganization(BaseTestCase):

    def create_organization(self, type_id, parent_id=1):
        desc = object_faker.faker.text(max_nb_chars=20)
        name = object_faker.faker.name()
        self.assertPageRendered(endpoint=url_for('organization.create_view'),
                                method=self.test_client.post,
                                expect_contents=[name, desc],
                                data={"type": type_id,
                                      "name": name,
                                      "url": url_for('organization.index_view'),
                                      "description": desc,
                                      "parent": parent_id})
        return name, desc

    def test_view(self):
        with self.test_client:
            fixture.login_as_admin(self.test_client)
            self.assertPageRendered(endpoint=url_for('organization.index_view'),
                                    method=self.test_client.get,
                                    expect_contents=['betterlife', '1', u'直营店'])

    def test_edit(self):

        from psi.app.models import EnumValues
        type_id = EnumValues.get(const.DIRECT_SELLING_STORE_ORG_TYPE_KEY).id

        with self.test_client:
            fixture.login_as_admin(self.test_client)
            desc = object_faker.faker.text(max_nb_chars=20)
            name = object_faker.faker.name()
            self.assertPageRendered(endpoint=self.edit_endpoint(view='organization'),
                                    method=self.test_client.post,
                                    expect_contents=[name, desc],
                                    data={"type": type_id, "name": name,
                                          "description": desc, "parent": u'__None'})

            self.create_organization(type_id, parent_id=1)
            self.create_organization(type_id, parent_id=2)
            self.create_organization(type_id, parent_id=3)

            desc = object_faker.faker.text(max_nb_chars=20)
            name = object_faker.faker.name()
            self.assertPageRendered(endpoint=url_for('organization.edit_view', id=4, url=url_for('organization.index_view')),
                                    method=self.test_client.post,
                                    expect_contents=[name, desc],
                                    data={"type": type_id,
                                          "name": name,
                                          "description": desc,
                                          "parent": 1})

    def test_create(self):
        from psi.app.models import EnumValues
        type_id = EnumValues.get(const.DIRECT_SELLING_STORE_ORG_TYPE_KEY).id

        with self.test_client:
            fixture.login_as_admin(self.test_client)
            org_name = object_faker.faker.name()
            org_desc = object_faker.faker.text(max_nb_chars=20)
            create_url = self.create_endpoint(view='organization')
            self.assertPageRendered(endpoint=create_url,
                                    method=self.test_client.get,
                                    expect_contents=['betterlife', '直营店'])
            self.assertPageRendered(endpoint=create_url,
                                    method=self.test_client.post,
                                    expect_contents=[org_name, org_desc],
                                    data={"type": type_id, "name": org_name, "description": org_desc, "parent": 1})
            self.assertDeleteSuccessful(endpoint=url_for('organization.delete_view', id=2, url=url_for('organization.index_view')),
                                        deleted_data=[org_name, org_desc])

            from psi.app.models import Organization
            user, pwd = object_faker.user(role_names=['organization_create', 'organization_view',
                                                      'organization_delete', 'organization_edit'],
                                          organization=Organization.query.get(1))
            db_util.save_objects_commit(user)
            fixture.login_user(self.test_client, user.email, pwd)
            from psi.app.models import EnumValues
            org_type = EnumValues.get(const.DIRECT_SELLING_STORE_ORG_TYPE_KEY)
            self.assertCreateFail(endpoint=create_url,
                                  create_data=[org_name, org_desc],
                                  data={"type": org_type.id, "name": org_name,
                                        "description": org_desc, "parent": 1})

    def test_delete_root_not_allowed(self):
        from psi.app.models import EnumValues
        type_id = EnumValues.get(const.DIRECT_SELLING_STORE_ORG_TYPE_KEY).id

        with self.test_client:
            fixture.login_as_admin(self.test_client)
            name = object_faker.faker.name()
            desc = object_faker.faker.text(max_nb_chars=20)
            self.assertPageRendered(endpoint=url_for('organization.edit_view', id=1, url=url_for('organization.index_view')),
                                    method=self.test_client.post,
                                    expect_contents=[name, desc],
                                    data={"type": type_id,
                                          "name": name,
                                          "description": desc,
                                          "parent": u'__None'})
            self.assertPageRendered(endpoint=url_for('organization.delete_view', url=url_for('organization.index_view'), id=1),
                                    method=self.test_client.post,
                                    expect_contents=[name, desc, "1"],
                                    data={"type": type_id,
                                          "name": name,
                                          "description": desc,
                                          "parent": u'__None'})

    def test_delete_normal_allowed(self):
        from psi.app.models import EnumValues
        type_id = EnumValues.get(const.DIRECT_SELLING_STORE_ORG_TYPE_KEY).id
        with self.test_client:
            fixture.login_as_admin(self.test_client)
            name, desc = self.create_organization(type_id=type_id, parent_id=1)
            self.assertDeleteSuccessful(endpoint=url_for('organization.delete_view', id=2, url=url_for('organization.index_view')),
                                        deleted_data=[name, desc])

    def test_delete_with_child_not_allowed(self):
        from psi.app.models import EnumValues, Organization
        type_id = EnumValues.get(const.DIRECT_SELLING_STORE_ORG_TYPE_KEY).id
        with self.test_client:
            fixture.login_as_admin(self.test_client)
            name1, desc1 = self.create_organization(type_id=type_id, parent_id=1)
            self.create_organization(type_id=type_id, parent_id=2)
            self.assertDeleteFail(endpoint=url_for('organization.delete_view', id=2, url=url_for('organization.index_view')),
                                  deleted_data=[name1, desc1])
            org = Organization.query.get(2)
            self.assertIsNotNone(org)
