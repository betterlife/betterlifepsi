from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.fixture import run_as_admin


class TestOpenDashboardPage(BaseTestCase):

    def test_open_dashboard(self):

        def test_logic():
            rv = self.test_client.get('/admin')
            self.assertEqual(301, rv.status_code)
            rv = self.test_client.get('/admin/')
            self.assertAlmostEquals('utf-8', rv.charset)
            self.assertEqual(200, rv.status_code)

        run_as_admin(self.test_client, test_logic)
