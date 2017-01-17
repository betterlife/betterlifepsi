import unittest

import random

from app import const
from app.utils import db_util
from tests import fixture
from tests.base_test_case import BaseTestCase
from tests.fixture import run_as_admin
from tests.object_faker import object_faker


class TestOpenDashboardPage(BaseTestCase):
    def setUp(self):
        self.app = fixture.init_app()
        self.test_client = self.app.test_client()
        self.app_context = self.app.test_request_context()
        self.app_context.push()

    def tearDown(self):
        fixture.cleanup_database(self.app_context)
        self.app_context.pop()

    def test_open_dashboard(self):

        def test_logic():
            rv = self.test_client.get('/admin')
            self.assertEqual(301, rv.status_code)
            rv = self.test_client.get('/admin/')
            self.assertAlmostEquals('utf-8', rv.charset)
            self.assertEqual(200, rv.status_code)

        run_as_admin(self.test_client, test_logic)
