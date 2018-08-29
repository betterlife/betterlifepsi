from flask import url_for
from flask_admin.consts import ICON_TYPE_GLYPH
from flask_babelex import lazy_gettext
from wtforms import ValidationError

from tests.fixture import run_as_admin
from tests.object_faker import object_faker
from psi.app.const import DIRECT_PO_TYPE_KEY, PO_ISSUED_STATUS_KEY, \
    RECEIVING_DRAFT_STATUS_KEY, RECEIVING_COMPLETE_STATUS_KEY
from tests.base_test_case import BaseTestCase


class TestReceivingAdmin(BaseTestCase):

    def test_delete_complete_receiving_not_allowed(self):
        def test_logic():
            from psi.app.models import Receiving, EnumValues
            from psi.app.views import ReceivingAdmin
            from psi.app.service import Info
            receiving = Receiving()
            complete_status = EnumValues.get(RECEIVING_COMPLETE_STATUS_KEY)
            receiving.status = complete_status
            db_session = Info.get_db().session
            receiving_admin = ReceivingAdmin(Receiving, db_session, name=lazy_gettext("Receiving"),
                                             category=lazy_gettext('Purchase'), menu_icon_type=ICON_TYPE_GLYPH,
                                             menu_icon_value='glyphicon-import')

            self.assertRaises(ValidationError, receiving_admin.on_model_delete, receiving)

        run_as_admin(self.test_client, test_logic)

    def test_receiving_pages(self):
        from psi.app.models.enum_values import EnumValues
        from psi.app.utils import db_util
        def test_logic():
            type = EnumValues.get(DIRECT_PO_TYPE_KEY)
            status = EnumValues.get(PO_ISSUED_STATUS_KEY)
            receiving_status = EnumValues.get(RECEIVING_DRAFT_STATUS_KEY)
            date = object_faker.faker.date_time_this_year()
            po = object_faker.purchase_order(number_of_line=2, type=type, status=status)
            db_util.save_objects_commit(po)
            remark = object_faker.faker.text(max_nb_chars=50)
            list_expect = [receiving_status.display, date.strftime("%Y-%m-%d"), remark,
                                      po.supplier.name, po.order_date.strftime("%Y-%m-%d"),
                                      po.remark]
            edit_expect = [receiving_status.display, date.strftime("%Y-%m-%d"), remark,]

            # Crete new receiving
            self.assertPageRendered(method=self.test_client.post,
                                    data=dict(purchase_order=po.id,
                                              status=receiving_status.id,
                                              create_lines='y',
                                              date=date, remark=remark),
                                    endpoint=self.create_endpoint(view='receiving'),
                                    expect_contents=list_expect)

            self.assertPageRendered(expect_contents=edit_expect,
                                    endpoint=self.edit_endpoint(view='receiving'))

            # Edit existing receiving
            new_remark = object_faker.faker.text(max_nb_chars=50)
            new_receive_date = object_faker.faker.date_time_this_year()
            complete_status = EnumValues.get(RECEIVING_COMPLETE_STATUS_KEY)
            new_expected = [complete_status.display, new_receive_date.strftime("%Y-%m-%d"),
                            new_remark, po.supplier.name, po.order_date.strftime("%Y-%m-%d"),
                            po.remark]

            self.assertPageRendered(method=self.test_client.post,
                                    endpoint=self.edit_endpoint(view='receiving'),
                                    data=dict(date=new_receive_date,
                                              status=complete_status.id,
                                              remark=new_remark),
                                    expect_contents=new_expected)

            # Detail page
            self.assertPageRendered(method=self.test_client.get,
                                    endpoint=self.details_endpoint(view='receiving'),
                                    expect_contents=new_expected)

        run_as_admin(self.test_client, test_logic)

    def test_delete_completed_receiving_not_allowed(self):
        from psi.app.models.enum_values import EnumValues
        from psi.app.utils import db_util
        def test_logic():
            type = EnumValues.get(DIRECT_PO_TYPE_KEY)
            status = EnumValues.get(PO_ISSUED_STATUS_KEY)
            draft_status = EnumValues.get(RECEIVING_DRAFT_STATUS_KEY)
            date = object_faker.faker.date_time_this_year()
            po = object_faker.purchase_order(number_of_line=2, type=type,
                                             status=status)
            db_util.save_objects_commit(po)
            remark = object_faker.faker.text(max_nb_chars=50)

            # Crete new receiving
            self.assertPageRendered(method=self.test_client.post,
                                    data=dict(purchase_order=po.id,
                                              status=draft_status.id,
                                              create_lines='y',
                                              date=date, remark=remark),
                                    endpoint=self.create_endpoint(view='receiving'),)

            # Change status to complete
            new_remark = object_faker.faker.text(max_nb_chars=50)
            new_receive_date = object_faker.faker.date_time_this_year()
            complete_status = EnumValues.get(RECEIVING_COMPLETE_STATUS_KEY)

            self.assertPageRendered(method=self.test_client.post,
                                    endpoint=self.edit_endpoint(view='receiving'),
                                    data=dict(date=new_receive_date,
                                              status=complete_status.id,
                                              remark=new_remark),)

            # Should not delete existing receiving with complete status
            endpoint = url_for('receiving.delete_view', id='1')
            data = dict(url=url_for('receiving.index_view'), id='1')
            rv = self.assertPageRendered(method=self.test_client.post,
                                         endpoint=endpoint, data=data)
            self.assertIn(complete_status.display.encode('utf-8'), rv.data)
            self.assertIn(new_receive_date.strftime("%Y-%m-%d").encode('utf-8'), rv.data)
            self.assertIn(new_remark.encode('utf-8'), rv.data)
            self.assertIn(po.supplier.name.encode('utf-8'), rv.data)
            self.assertIn(po.order_date.strftime("%Y-%m-%d").encode('utf-8'),rv.data)
            self.assertIn(po.remark.encode('utf-8'), rv.data)
            self.assertIn(b'You are not allowed to delete this object', rv.data)

        run_as_admin(self.test_client, test_logic)
