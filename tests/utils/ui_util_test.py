# encoding=utf-8
import unittest


class TestUIUtil(unittest.TestCase):
    def test_render_version(self):
        from app.utils.ui_util import render_version
        result = render_version()
        self.assertIn("""Build: <a href="https://travis-ci.org/betterlife/psi/builds/144799860" target="_blank">254</a>,""", result)
        self.assertIn("""Commit: <a href="https://github.com/betterlife/psi/commit/8ab8044" target="_blank">8ab8044</a>,""", result)
        self.assertIn("""Branch: master,""", result)
        self.assertIn("""Tag: None,""", result)
        self.assertIn("""Date: 2016.7.14""", result)
