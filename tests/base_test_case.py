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

    def assertPageRendered(self, endpoint, method=None, data=None, expect_contents=None):
        if method is None:
            method = self.test_client.get
        rv = method(endpoint, data=data, follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        if expect_contents is not None:
            for c in expect_contents:
                self.assertIn(c, rv.data)
        return rv

    def assertCreateFail(self, endpoint, data=None, create_data=None):
        return self.assertDataNotInResponse(data, endpoint, create_data)

    def assertDeleteSuccessful(self, endpoint, data=None, deleted_data=None):
        return self.assertDataNotInResponse(data, endpoint, deleted_data)

    def assertDataNotInResponse(self, data, endpoint, not_expect_contents):
        rv = self.test_client.post(endpoint, data=data, follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        if not_expect_contents is not None:
            for c in not_expect_contents:
                self.assertNotIn(c, rv.data)
        return rv

    def assertDeleteFail(self, endpoint, data=None, deleted_data=None):
        rv = self.test_client.post(endpoint, data=data, follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        if deleted_data is not None:
            for c in deleted_data:
                self.assertIn(c, rv.data)
        return rv


