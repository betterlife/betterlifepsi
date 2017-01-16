import unittest

from tests import fixture
from tests.object_faker import object_faker


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = fixture.init_app()
        self.test_client = self.app.test_client()
        self.app_context = self.app.test_request_context()
        self.app_context.push()

    def tearDown(self):
        fixture.cleanup_database(self.app_context)
        self.app_context.pop()

    def assert_page_render_correct(self, method, endpoint):
        rv = method(endpoint, follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        return rv
