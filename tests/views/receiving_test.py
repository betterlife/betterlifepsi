from flask_admin.consts import ICON_TYPE_GLYPH
from flask_babelex import lazy_gettext
from wtforms import ValidationError

from tests import fixture
from tests.base_test_case import BaseTestCase


class TestReceivingAdmin(BaseTestCase):

    def test_on_model_delete(self):
        from app.models import Receiving, EnumValues
        from app.views import ReceivingAdmin
        from app import const
        from app.service import Info
        fixture.login_as_admin(self.test_client)
        receiving = Receiving()
        complete_status = EnumValues.get(const.RECEIVING_COMPLETE_STATUS_KEY)
        receiving.status = complete_status
        db_session = Info.get_db().session
        receiving_admin = ReceivingAdmin(Receiving, db_session, name=lazy_gettext("Receiving"),
                                         category=lazy_gettext('Purchase'), menu_icon_type=ICON_TYPE_GLYPH,
                                         menu_icon_value='glyphicon-import')

        self.assertRaises(ValidationError, receiving_admin.on_model_delete, receiving)
