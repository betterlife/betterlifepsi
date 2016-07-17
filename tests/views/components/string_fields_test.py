# encoding=utf-8
import unittest

from tests import fixture


class TestDisabledStringField(unittest.TestCase):
    def setUp(self):
        self.test_client = fixture.init_app().test_client()

    def DisabledStringField_test(self):
        from wtforms import form
        from app.views.components import DisabledStringField

        class SimpleForm(form.Form):
            df = DisabledStringField()

        simple_form = SimpleForm(df='df', rf='rf', ctf='ctf')
        self.assertEqual('<input disabled id="df" name="df" type="text" value="df">', str(simple_form.df))


class TestReadonlyStringField(unittest.TestCase):
    def setUp(self):
        self.test_client = fixture.init_app().test_client()

    def DisabledStringField_test(self):
        from wtforms import form
        from app.views.components import ReadonlyStringField

        class SimpleForm(form.Form):
            rf = ReadonlyStringField()

        simple_form = SimpleForm(df='df', rf='rf', ctf='ctf')
        self.assertEqual('<input id="rf" name="rf" readonly="readonly" type="text" value="rf">', str(simple_form.rf))


class TestCKTextAreaField(unittest.TestCase):
    def setUp(self):
        self.test_client = fixture.init_app().test_client()

    def DisabledStringField_test(self):
        from wtforms import form
        from app.views.components import CKTextAreaField

        class SimpleForm(form.Form):
            ctf = CKTextAreaField()

        simple_form = SimpleForm(df='df', rf='rf', ctf='ctf')
        self.assertEqual('<textarea class="ckeditor" id="ctf" name="ctf">ctf</textarea>', str(simple_form.ctf))
