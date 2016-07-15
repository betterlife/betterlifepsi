import unittest

from flask.ext.admin.consts import ICON_TYPE_GLYPH
from flask.ext.babelex import lazy_gettext
from wtforms import ValidationError

from tests import fixture


class TestReceivingAdmin(unittest.TestCase):
    def setUp(self):
        self.app = fixture.init_app()
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        fixture.login_as_admin(self.test_client)

    def tearDown(self):
        fixture.cleanup_database(self.app_context)
        self.app_context.pop()

    def test_on_model_delete(self):
        from app.models import Receiving, EnumValues
        from app.views.receiving import ReceivingAdmin
        from app import const
        from app.service import Info
        receiving = Receiving()
        complete_status = EnumValues.find_one_by_code(const.RECEIVING_COMPLETE_STATUS_KEY)
        receiving.status = complete_status
        db_session = Info.get_db().session
        receiving_admin = ReceivingAdmin(Receiving, db_session, name=lazy_gettext("Receiving"),
                                         category=lazy_gettext('Purchase'), menu_icon_type=ICON_TYPE_GLYPH,
                                         menu_icon_value='glyphicon-import')

        self.assertRaises(ValidationError, receiving_admin.on_model_delete, receiving)
