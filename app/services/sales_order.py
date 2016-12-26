from app.models import Preference, Incoming, EnumValues, ShippingLine


class SalesOrderService(object):

    @staticmethod
    def create_or_update_shipping(sales_order):
        status = EnumValues.find_one_by_code('SHIPPING_COMPLETE')
        shipping = sales_order.so_shipping
        if shipping is None:
            from app.models import Shipping
            shipping = Shipping()
        shipping.date = sales_order.order_date
        shipping.sales_order = sales_order
        shipping.status = status
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
        from app.models import Preference
        preference = Preference.get()
        if (sales_order.logistic_amount is not None) and (sales_order.logistic_amount > 0):
            from app.models import Expense
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
