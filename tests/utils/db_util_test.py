import unittest

from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.object_faker import object_faker


class TestDbUtil(BaseTestCase):

    def test_get_next_id(self):
        from psi.app.utils import db_util
        from psi.app.models import Supplier
        next_id = db_util.get_next_id(Supplier)
        self.assertEquals(1, next_id)

    def test_get_next_id_with_existing_one(self):
        from psi.app.utils import db_util
        from psi.app.models import ProductCategory
        with self.test_client:
            fixture.login_as_admin(self.test_client)
            object_faker.category()
            next_id = db_util.get_next_id(ProductCategory)
            self.assertEquals(3, next_id)
