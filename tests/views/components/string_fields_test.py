# encoding=utf-8
import unittest

from tests import fixture


class TestDisabledStringField(unittest.TestCase):
    def setUp(self):
        self.test_client = fixture.init_app().test_client()

    def DisabledStringField_test(self):
        from wtforms import form
        from psi.app.views.components import DisabledStringField

        class SimpleForm(form.Form):
            df = DisabledStringField()

        simple_form = SimpleForm(df='df', rf='rf', ctf='ctf')
        self.assertEqual('<input disabled id="df" name="df" type="text" value="df">', str(simple_form.df))


class TestReadonlyStringField(unittest.TestCase):
    def setUp(self):
        self.test_client = fixture.init_app().test_client()

    def DisabledStringField_test(self):
        from wtforms import form
        from psi.app.views.components import ReadonlyStringField

        class SimpleForm(form.Form):
            rf = ReadonlyStringField()

        simple_form = SimpleForm(df='df', rf='rf', ctf='ctf')
        self.assertEqual('<input id="rf" name="rf" readonly="readonly" type="text" value="rf">', str(simple_form.rf))


class TestHiddenStringField(unittest.TestCase):
    def setUp(self):
        self.test_client = fixture.init_app().test_client()

    def DisabledStringField_test(self):
        from wtforms import form
        from psi.app.views.components import HiddenField

        class SimpleForm(form.Form):
            hf = HiddenField()

        simple_form = SimpleForm(hf='hf')
        self.assertEqual('<input id="hf" name="hf" type="hidden" value="hf">', str(simple_form.hf))


class TestCKTextAreaField(unittest.TestCase):
    def setUp(self):
        self.test_client = fixture.init_app().test_client()

    def DisabledStringField_test(self):
        from wtforms import form
        from psi.app.views.components import CKTextAreaField

        class SimpleForm(form.Form):
            ctf = CKTextAreaField()

        simple_form = SimpleForm(df='df', rf='rf', ctf='ctf')
        self.assertEqual('<textarea class="ckeditor" id="ctf" name="ctf">ctf</textarea>', str(simple_form.ctf))


class TestDisabledBooleanField(unittest.TestCase):
    def setUp(self):
        self.test_client = fixture.init_app().test_client()

    def DisabledStringField_test(self):
        from wtforms import form
        from psi.app.views.components import DisabledBooleanField

        class SimpleForm(form.Form):
            dbf = DisabledBooleanField()

        simple_form = SimpleForm(dbf="dbf")
        self.assertEqual('<input checked disabled id="dbf" name="dbf" type="checkbox" value="y">', str(simple_form.dbf))
