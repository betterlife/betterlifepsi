# encoding=utf-8
from flask_restful import Resource, reqparse
from app.service import Info
from app.models import EnumValues, SalesOrder
from app.const import SO_STATUS_KEY, SO_CREATED_STATUS_KEY
from app.utils import has_role

parser = reqparse.RequestParser()
parser.add_argument('status_id', type=int, help='ID of new status')


class SalesOrderApi(Resource):

    @has_role("franchise_sales_order_edit")
    def put(self, sales_order_id):
        args = parser.parse_args()
        status_id = args['status_id']
        session = Info.get_db().session
        sales_order = session.query(SalesOrder).get(sales_order_id)
        status = session.query(EnumValues).get(status_id)
        if status is not None and status.type.code == SO_STATUS_KEY:
            if sales_order.status.code == SO_CREATED_STATUS_KEY:
                sales_order.status_id = status_id
                session.add(sales_order)
                session.commit()
                return {'message': 'Status update successfully'}, 200
            else:
                return {'message': 'Status update not allowed'}, 201
        else:
            return {'message': 'Invalid sales order status parameter'}, 201
