# coding=utf-8
from flask import url_for

from psi.app import const
from psi.app.utils import db_util
from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker


class BaseOrganizationTestCase(BaseTestCase):

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
