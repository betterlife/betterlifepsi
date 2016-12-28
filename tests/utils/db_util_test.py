import unittest

from tests import fixture
from tests.object_faker import object_faker


class TestDbUtil(unittest.TestCase):
    def setUp(self):
        self.app = fixture.init_app()
        self.test_client = self.app.test_client()
        self.app_context = self.app.test_request_context()
        self.app_context.push()

    def tearDown(self):
        fixture.cleanup_database(self.app_context)
        self.app_context.pop()

    def test_get_next_id(self):
        from app.utils import db_util
        from app.models import Supplier
        next_id = db_util.get_next_id(Supplier)
        self.assertEquals(1, next_id)

    def test_get_next_id_with_existing_one(self):
        from app.utils import db_util
        from app.models import ProductCategory
        with self.test_client:
            fixture.login_as_admin(self.test_client)
            object_faker.category()
            next_id = db_util.get_next_id(ProductCategory)
            self.assertEquals(3, next_id)
