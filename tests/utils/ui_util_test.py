# encoding=utf-8
from flask import current_app

from tests import fixture
from tests.base_test_case import BaseTestCase


class TestUIUtil(BaseTestCase):

    def test_render_version(self):
        from psi.app.utils.ui_util import render_version
        import os
        fixture.login_as_admin(self.test_client)
        my_dir = os.path.dirname(os.path.realpath(__file__))
        result = render_version(swtag_file=my_dir + "/../resources/swtag")
        self.assertIn("""Build: <a href="{url}/8ab8044" target="_blank">-</a>,""".format(url=current_app.config['BUILDER_URL_PREFIX']), result)
        self.assertIn("""Commit: <a href="{url}/8ab8044" target="_blank">8ab8044</a>,""".format(url=current_app.config['GIT_URL_PREFIX']), result)
        self.assertIn("""Branch: master,""", result)
        self.assertIn("""Tag: V0.6.5,""", result)
        self.assertIn("""Date: 2016.7.14""", result)
