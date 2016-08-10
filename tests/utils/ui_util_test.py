# encoding=utf-8
import unittest
from flask import current_app
from tests import fixture


class TestUIUtil(unittest.TestCase):

    def setUp(self):
        self.app = fixture.init_app()
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        fixture.login_as_admin(self.test_client)

    def tearDown(self):
        fixture.cleanup_database(self.app_context)
        self.app_context.pop()

    def test_render_version(self):
        from app.utils.ui_util import render_version
        result = render_version()
        self.assertIn("""Build: <a href="{url}/144799860" target="_blank">254</a>,""".format(url=current_app.config['BUILDER_URL_PREFIX']), result)
        self.assertIn("""Commit: <a href="{url}/8ab8044" target="_blank">8ab8044</a>,""".format(url=current_app.config['GIT_URL_PREFIX']), result)
        self.assertIn("""Branch: master,""", result)
        self.assertIn("""Tag: None,""", result)
        self.assertIn("""Date: 2016.7.14""", result)
