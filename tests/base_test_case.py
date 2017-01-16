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

    def assertPageRenderCorrect(self, endpoint, method=None, data=None, expect_content=None):
        if method is None:
            method = self.test_client.get
        rv = method(endpoint, data=data, follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        if expect_content is not None:
            for c in expect_content:
                self.assertIn(c, rv.data)
        return rv
