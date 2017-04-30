from psi.app import const
from psi.app.models import Incoming, EnumValues, ShippingLine, Shipping, RelatedValues, PurchaseOrder
from psi.app.service import Info


class SalesOrderService(object):

    @staticmethod
    def create_or_update_shipping(sales_order):
        status = EnumValues.get(const.SHIPPING_COMPLETE_STATUS_KEY)
        shipping = sales_order.so_shipping
        if shipping is None:
            shipping = Shipping()
        shipping.date = sales_order.order_date
        shipping.sales_order = sales_order
        shipping.status = status
        if sales_order.type.code == const.DIRECT_SO_TYPE_KEY:
            shipping.type = EnumValues.get(const.DIRECT_SHIPPING_TYPE_KEY)
        elif sales_order.type.code == const.FRANCHISE_SO_TYPE_KEY:
            shipping.type = EnumValues.get(const.FRANCHISE_SHIPPING_TYPE_KEY)
        shipping.organization = sales_order.organization
        for line in sales_order.lines:
            new_sl = None
            for old_sl in shipping.lines:
                if old_sl.sales_order_line_id == line.id:
                    new_sl = old_sl
                    break
            new_sl = SalesOrderService.copy_sales_order_line_to_shipping_line(line, new_sl)
            new_sl.shipping = shipping
        shipping.create_or_update_inventory_transaction()
        return shipping

    @staticmethod
    def copy_sales_order_line_to_shipping_line(sales_order_line, sl):
        if sl is None:
            sl = ShippingLine()
        sl.quantity = sales_order_line.quantity
        sl.price = sales_order_line.unit_price
        sl.product = sales_order_line.product
        sl.sales_order_line = sales_order_line
        return sl

    @staticmethod
    def create_or_update_incoming(sales_order):
        incoming = sales_order.incoming
        default_so_incoming_status = EnumValues.get(const.DEFUALT_SALES_ORDER_INCOMING_STATUS_KEY)
        default_so_incoming_type = EnumValues.get(const.DEFUALT_SALES_ORDER_INCOMING_TYPE_KEY)
        incoming = SalesOrderService.create_associated_obj(incoming, sales_order,
                                                           default_obj=Incoming(),
                                                           value=sales_order.actual_amount,
                                                           status_id=default_so_incoming_status.id,
                                                           type_id=default_so_incoming_type.id)
        return incoming

    @staticmethod
    def create_or_update_expense(sales_order):
        expense = sales_order.expense
        default_so_expense_status_id = EnumValues.get(const.DEFUALT_SALES_ORDER_EXPENSE_STATUS_KEY).id
        default_so_expense_type_id = EnumValues.get(const.DEFUALT_SALES_ORDER_EXPENSE_TYPE_KEY).id
        if (sales_order.logistic_amount is not None) and (sales_order.logistic_amount > 0):
            from psi.app.models import Expense
            default_obj = Expense(sales_order.logistic_amount, sales_order.order_date,
                                  default_so_expense_status_id, default_so_expense_type_id)
            expense = SalesOrderService.create_associated_obj(expense, sales_order,
                                                            default_obj=default_obj,
                                                            value=sales_order.logistic_amount,
                                                            status_id=default_so_expense_status_id,
                                                            type_id=default_so_expense_type_id)
        return expense

    @staticmethod
    def create_associated_obj(obj, sales_order, default_obj, value, status_id, type_id):
        if obj is None:
            obj = default_obj
            obj.status_id = status_id
            obj.category_id = type_id
        obj.amount = value
        obj.sales_order = sales_order
        obj.date = sales_order.order_date
        obj.organization = sales_order.organization
        return obj

    @staticmethod
    def get_related_po(sales_order):
        rt = EnumValues.get(const.FRANCHISE_PO_TO_SO_RT_KEY)
        session = Info.get_db().session
        related_value, purchase_order = None, None
        if sales_order.type.code == const.FRANCHISE_SO_TYPE_KEY:
            related_value = session.query(RelatedValues).filter_by(to_object_id=sales_order.id, relation_type_id=rt.id).first()
        if related_value is not None:
            purchase_order = session.query(PurchaseOrder).get(related_value.from_object_id)
        return purchase_order

    @staticmethod
    def update_related_po_status(sales_order, status_code):
        purchase_order = SalesOrderService.get_related_po(sales_order)
        session = Info.get_db().session
        if purchase_order is not None:
            status = EnumValues.get(status_code)
            purchase_order.status = status
            session.add(purchase_order)
        return purchase_order