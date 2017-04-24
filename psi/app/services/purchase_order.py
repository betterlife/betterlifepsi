from psi.app import const, service


class PurchaseOrderService(object):
    @staticmethod
    def create_expense_receiving(po):
        if po.status.code == const.PO_ISSUED_STATUS_KEY:
            logistic_exp, goods_exp = PurchaseOrderService.create_expenses(po)
            db = service.Info.get_db()
            if logistic_exp is not None:
                db.session.add(logistic_exp)
            if goods_exp is not None:
                db.session.add(goods_exp)
            receiving = PurchaseOrderService.create_receiving_if_not_exist(po)
            if receiving is not None:
                db.session.add(receiving)
            return logistic_exp, goods_exp, receiving

    @staticmethod
    def create_expenses(po):
        """
        Create expense from purchase order
        Create one record for the goods amount, one record for logistic amount
        :return: The logistic expense and goods expense
        """
        from psi.app.models import Expense, Preference
        expenses = po.expenses
        logistic_exp = None
        preference = Preference.get()
        goods_exp = None
        if expenses is None:
            expenses = dict()
        for expense in expenses:
            if (expense.category_id == preference.def_po_logistic_exp_type_id) and (po.logistic_amount != 0):
                logistic_exp = expense
                logistic_exp.amount = po.logistic_amount
            elif (expense.category_id == preference.def_po_goods_exp_type_id) and (po.goods_amount != 0):
                goods_exp = expense
                goods_exp.amount = po.goods_amount
        if (logistic_exp is None) and (po.logistic_amount is not None and po.logistic_amount != 0):
            logistic_exp = Expense(po.logistic_amount, po.order_date,
                                   preference.def_po_logistic_exp_status_id,
                                   preference.def_po_logistic_exp_type_id)
        if (goods_exp is None) and (po.goods_amount is not None and po.goods_amount != 0):
            goods_exp = Expense(po.goods_amount, po.order_date,
                                preference.def_po_goods_exp_status_id,
                                preference.def_po_goods_exp_type_id)
        if logistic_exp is not None:
            logistic_exp.purchase_order = po
            logistic_exp.organization = po.organization
        if goods_exp is not None:
            goods_exp.purchase_order = po
            goods_exp.organization = po.organization
        return logistic_exp, goods_exp

    @staticmethod
    def create_receiving_if_not_exist(po):
        """
        Draft receiving document is created from purchase order only
         if there's no associated receiving exists for this PO.
        :param model: the Purchase order model
        :return: Receiving document if a new one created, or None
        """
        from psi.app.models import Receiving
        receivings = po.po_receivings
        if receivings is None or len(receivings) == 0:
            recv = Receiving.create_draft_recv_from_po(po)
            return recv
        return None
