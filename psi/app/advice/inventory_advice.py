# coding=utf-8
from psi.app.utils import format_decimal


class InventoryAdvice(object):
    @staticmethod
    def advice(product):
        lead_deliver_day = format_decimal(product.get_lead_deliver_day())

        if product.available_quantity < 0:
            return u"""<span class="i_a_warning i_a_number">库存错误</span>，
                      请立即<a href="/admin/inventorytransaction/new" target="_blank">修正该错误</a>"""
        if product.available_quantity == 0 and product.weekly_sold_qty != 0:
            return u'库存为<span class="i_a_warning i_a_number">0</span>，请立即补货, ' \
                   u'补货需要<span class="i_a_warning i_a_number">' \
                   + str(lead_deliver_day) + u'</span>天，' \
                   + u'补货期间损失利润:<span class="i_a_warning i_a_number">' \
                   + str(format_decimal(product.get_profit_lost_caused_by_inventory_short())) \
                   + u'</span>元，' \
                   + u'<a href="/admin/dpo/new/" target="_blank">点此补货</a>'
        elif product.weekly_sold_qty > 0:
            can_sell_day = format_decimal(product.available_quantity / (product.weekly_sold_qty/7))
            if can_sell_day > lead_deliver_day:
                return u'当前库存可供销售<span class="i_a_number">' + str(can_sell_day) + "</span>天"
            elif can_sell_day < lead_deliver_day and product.in_transit_quantity == 0:
                return u'当前库存在新货品到达前即会售完，可销售<span class="i_a_number">' \
                       + str(can_sell_day) + u'</span>天' \
                       + u', 补货需要<span class="i_a_number">' + str(lead_deliver_day) + '</span>天，' \
                       + u'补货期间损失利润额<span class="i_a_number i_a_warning">' \
                       + str(format_decimal(product.get_profit_lost_caused_by_inventory_short())) \
                       + u'</span>元，' \
                       + u'<a href="/admin/dpo/new/" target="_blank">点此补货</a>'
        else:
            return u'-'
