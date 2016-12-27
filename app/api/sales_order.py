# encoding=utf-8
from flask_restful import Resource, reqparse

from app.models import RelatedValues
from app.service import Info
from app.models import EnumValues, SalesOrder
from app.const import SO_STATUS_KEY, SO_CREATED_STATUS_KEY, FRANCHISE_PO_TO_SO_RT_KEY, PO_SHIPPED_STATUS_KEY
from app.utils import has_role, db_util

parser = reqparse.RequestParser()
parser.add_argument('status_id', type=int, help='ID of new status')


class SalesOrderApi(Resource):

    @has_role("franchise_sales_order_edit")
    def put(self, sales_order_id):
        try:
            args = parser.parse_args()
            status_id = args['status_id']
            session = Info.get_db().session
            sales_order = session.query(SalesOrder).get(sales_order_id)
            status = session.query(EnumValues).get(status_id)
            rt = EnumValues.find_one_by_code(FRANCHISE_PO_TO_SO_RT_KEY)
            po_shipped = EnumValues.find_one_by_code(PO_SHIPPED_STATUS_KEY)
            if status is not None and status.type.code == SO_STATUS_KEY:
                if sales_order.status.code == SO_CREATED_STATUS_KEY:
                    sales_order.status_id = status_id
                    purchase_order = session.query(RelatedValues).filter_by(to_object_id=sales_order.id, relation_type_id=rt.id).first()
                    if purchase_order is not None:
                        purchase_order.status_id = po_shipped.id
                    db_util.save_objects_commit(sales_order, purchase_order)
                    return dict(message='Status update successfully', status='success'), 200
                else:
                    return dict(message='Status update not allowed', status='error'), 201
            else:
                return dict(message='Invalid sales order status parameter', status='error'), 201
        except:
            return dict(message='Failed to change sales order status', status='error'), 201

