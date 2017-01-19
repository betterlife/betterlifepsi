from psi.app.const import DIRECT_SHIPPING_TYPE_KEY, FRANCHISE_SHIPPING_TYPE_KEY, SHIPPING_COMPLETE_STATUS_KEY, \
    DIRECT_SO_TYPE_KEY, FRANCHISE_SO_TYPE_KEY, FRANCHISE_PO_TO_SO_RT_KEY
from psi.app.models import Preference, Incoming, EnumValues, ShippingLine, Shipping, RelatedValues, PurchaseOrder
from psi.app.service import Info


class SalesOrderService(object):

    @staticmethod
    def create_or_update_shipping(sales_order):
        status = EnumValues.find_one_by_code(SHIPPING_COMPLETE_STATUS_KEY)
        shipping = sales_order.so_shipping
        if shipping is None:
            shipping = Shipping()
        shipping.date = sales_order.order_date
        shipping.sales_order = sales_order
        shipping.status = status
        if sales_order.type.code == DIRECT_SO_TYPE_KEY:
            shipping.type = EnumValues.find_one_by_code(DIRECT_SHIPPING_TYPE_KEY)
        elif sales_order.type.code == FRANCHISE_SO_TYPE_KEY:
            shipping.type = EnumValues.find_one_by_code(FRANCHISE_SHIPPING_TYPE_KEY)
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
        sl.product_id = sales_order_line.product_id
        sl.sales_order_line_id = sales_order_line.id
        return sl

    @staticmethod
    def create_or_update_incoming(sales_order):
        incoming = sales_order.incoming
        preference = Preference.get()
        incoming = SalesOrderService.create_associated_obj(incoming, sales_order,
                                                           default_obj=Incoming(),
                                                           value=sales_order.actual_amount,
                                                           status_id=preference.def_so_incoming_status_id,
                                                           type_id=preference.def_so_incoming_type_id)
        return incoming

    @staticmethod
    def create_or_update_expense(sales_order):
        expense = sales_order.expense
        preference = Preference.get()
        if (sales_order.logistic_amount is not None) and (sales_order.logistic_amount > 0):
            from psi.app.models import Expense
            default_obj = Expense(sales_order.logistic_amount, sales_order.order_date,
                                  preference.def_so_exp_status_id, preference.def_so_exp_type_id)
            expense = SalesOrderService.create_associated_obj(expense, sales_order,
                                                            default_obj=default_obj,
                                                            value=sales_order.logistic_amount,
                                                            status_id=preference.def_so_exp_status_id,
                                                            type_id=preference.def_so_exp_type_id)
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
        rt = EnumValues.find_one_by_code(FRANCHISE_PO_TO_SO_RT_KEY)
        session = Info.get_db().session
        related_value, purchase_order = None, None
        if sales_order.type.code == FRANCHISE_SO_TYPE_KEY:
            related_value = session.query(RelatedValues).filter_by(to_object_id=sales_order.id, relation_type_id=rt.id).first()
        if related_value is not None:
            purchase_order = session.query(PurchaseOrder).get(related_value.from_object_id)
        return purchase_order

    @staticmethod
    def update_related_po_status(sales_order, status_code):
        purchase_order = SalesOrderService.get_related_po(sales_order)
        session = Info.get_db().session
        if purchase_order is not None:
            status = EnumValues.find_one_by_code(status_code)
            purchase_order.status = status
            session.add(purchase_order)
        return purchase_order