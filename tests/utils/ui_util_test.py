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
        self.assertIn(
            """Build: <a href="{url}/83772950" target="_blank">48</a>,""".format(
                url=current_app.config['BUILDER_URL_PREFIX']),
            result)
        self.assertIn(
            """Commit: <a href="{url}/7e57e7a" target="_blank">7e57e7a</a>,""".
            format(url=current_app.config['GIT_URL_PREFIX']),
            result)
        self.assertIn("""Branch: master,""", result)
        self.assertIn("""Tag: v0.6.7.post4,""", result)
        self.assertIn("""Date: 2018-09-04""", result)
