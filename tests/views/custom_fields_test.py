# encoding=utf-8
import unittest

from app import DbInfo
from tests import fixture


class TestCases(unittest.TestCase):
    def setUp(self):
        self.test_client = fixture.init_test_client()

    def DisabledStringField_test(self):
        from wtforms import form
        from app.views.custom_fields import DisabledStringField, ReadonlyStringField, CKTextAreaField

        class SimpleForm(form.Form):
            df = DisabledStringField()
            rf = ReadonlyStringField()
            ctf = CKTextAreaField()

        simple_form = SimpleForm(df='df', rf='rf', ctf='ctf')
        self.assertEqual('<input disabled id="df" name="df" type="text" value="df">', str(simple_form.df))
        self.assertEqual('<input id="rf" name="rf" readonly="readonly" type="text" value="rf">', str(simple_form.rf))
        self.assertEqual('<textarea class="ckeditor" id="ctf" name="ctf">ctf</textarea>', str(simple_form.ctf))
