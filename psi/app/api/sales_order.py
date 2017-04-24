# encoding=utf-8
from __future__ import print_function

from psi.app.const import *
from psi.app.models import EnumValues, SalesOrder
from psi.app.service import Info
from psi.app.utils import has_role, return_error_as_json
from flask_babelex import gettext
from flask_restful import Resource, reqparse

from psi.app.services import SalesOrderService

parser = reqparse.RequestParser()
parser.add_argument('status_id', type=int, help='ID of new status')


class SalesOrderApi(Resource):

    @has_role("franchise_sales_order_edit", return_error_as_json)
    def put(self, sales_order_id):
        try:
            args = parser.parse_args()
            status_id = args['status_id']
            session = Info.get_db().session
            sales_order = session.query(SalesOrder).get(sales_order_id)
            status = session.query(EnumValues).get(status_id)
            if status is not None and status.type.code == SO_STATUS_KEY:
                if sales_order.status.code == SO_CREATED_STATUS_KEY:
                    if status.code == SO_SHIPPED_STATUS_KEY or status.code == SO_DELIVERED_STATUS_KEY:
                        sales_order.status_id = status_id
                        shipping = SalesOrderService.create_or_update_shipping(sales_order)
                        session.add(sales_order)
                        session.add(shipping)
                        SalesOrderService.update_related_po_status(sales_order, PO_SHIPPED_STATUS_KEY)
                    elif status.code == SO_INVALID_STATUS_KEY:
                        sales_order.status_id = status_id
                        session.add(sales_order)
                        po = SalesOrderService.update_related_po_status(sales_order, PO_REJECTED_STATUS_KEY)
                        recvs = po.po_receivings
                        for recv in recvs:
                            session.delete(recv)
                    session.commit()
                    return dict(message=gettext('Status update successfully'), status='success'), 200
                else:
                    return dict(message=gettext('Status update not allowed'), status='error'), 201
            else:
                return dict(message=gettext('Invalid sales order status parameter'), status='error'), 201
        except Exception as e:
            return dict(message=gettext('Failed to change sales order status<br>{0}').format(e.message), status='error'), 201

