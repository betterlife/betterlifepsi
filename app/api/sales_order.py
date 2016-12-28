# encoding=utf-8
from __future__ import print_function
from flask_restful import Resource, reqparse

from app.models import RelatedValues
from app.service import Info
from app.models import EnumValues, SalesOrder, PurchaseOrder
from app.const import SO_STATUS_KEY, SO_CREATED_STATUS_KEY, FRANCHISE_PO_TO_SO_RT_KEY, PO_SHIPPED_STATUS_KEY, SO_TYPE_KEY
from app.services import SalesOrderService
from app.utils import has_role, db_util

parser = reqparse.RequestParser()
parser.add_argument('status_id', type=int, help='ID of new status')


class SalesOrderApi(Resource):

    def update_related_po(self, sales_order):
        rt = EnumValues.find_one_by_code(FRANCHISE_PO_TO_SO_RT_KEY)
        session = Info.get_db().session
        related_value, purchase_order = None, None
        if sales_order.type.code == SO_TYPE_KEY:
            related_value = session.query(RelatedValues).filter_by(to_object_id=sales_order.id, relation_type_id=rt.id).first()
        if related_value is not None:
            purchase_order = session.query(PurchaseOrder).get(related_value.from_object_id)
            if purchase_order is not None:
                po_shipped = EnumValues.find_one_by_code(PO_SHIPPED_STATUS_KEY)
                purchase_order.status = po_shipped
        return purchase_order


    @has_role("franchise_sales_order_edit")
    def put(self, sales_order_id):
        try:
            args = parser.parse_args()
            status_id = args['status_id']
            session = Info.get_db().session
            sales_order = session.query(SalesOrder).get(sales_order_id)
            status = session.query(EnumValues).get(status_id)
            if status is not None and status.type.code == SO_STATUS_KEY:
                if sales_order.status.code == SO_CREATED_STATUS_KEY:
                    sales_order.status_id = status_id
                    shipping = SalesOrderService.create_or_update_shipping(sales_order)
                    session.add(sales_order)
                    session.add(shipping)
                    po = self.update_related_po(sales_order)
                    if po is not None:
                        session.add(po)
                    session.commit() 
                    return dict(message='Status update successfully', status='success'), 200
                else:
                    return dict(message='Status update not allowed', status='error'), 201
            else:
                return dict(message='Invalid sales order status parameter', status='error'), 201
        except Exception as e:
            Info.get_logger().captureException()
            return dict(message='Failed to change sales order status<br>{0}'.format(e.message), status='error'), 201

