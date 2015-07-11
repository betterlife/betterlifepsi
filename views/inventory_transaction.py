from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext
from models import InventoryTransactionLine, InventoryTransaction
from views import ModelViewWithAccess, DisabledStringField


class InventoryTransactionLineInlineAdmin(InlineFormAdmin):

    form_args = dict(
        id=dict(label=lazy_gettext('id')),
        product=dict(label=lazy_gettext('Product')),
        price=dict(label=lazy_gettext('Inventory Transaction Price'),
                   description=lazy_gettext('For sales, it should be sell price, '
                                            'for item lost or broken, should be purchase price plus logistic expend')),
        in_transit_quantity=dict(label=lazy_gettext('In Transit Quantity'),
                                 description=lazy_gettext('Quantity of product ordered but still on the way')),
        quantity=dict(label=lazy_gettext('Actual Quantity Change'),
                      description=lazy_gettext('This quantity should be a negative number '
                                               'for sales, item lost or item broken')),
        remark=dict(label=lazy_gettext('Remark')),
    )

    def postprocess_form(self, form):
        form.total_amount = DisabledStringField(label=lazy_gettext('Total Amount'))
        form.itl_receiving_line = None
        form.remark = None
        form.itl_shipping_line = None
        return form

class InventoryTransactionAdmin(ModelViewWithAccess):

    can_delete = False

    column_list = ('id', 'type', 'date', 'total_amount', 'it_receiving', 'it_shipping', 'remark')

    column_sortable_list = ('id', ('type', 'type.display'), 'total_amount', 'date',)

    column_labels = {
        'id': lazy_gettext('id'),
        'type': lazy_gettext('Inventory Transaction Type'),
        'date': lazy_gettext('Date'),
        'total_amount': lazy_gettext('Total Amount'),
        'remark': lazy_gettext('Remark'),
        'lines': lazy_gettext('Lines'),
        'it_receiving': lazy_gettext('Related Receiving'),
        'it_shipping': lazy_gettext('Related Shipping'),
    }

    form_excluded_columns = ('it_shipping', 'it_receiving')

    form_args = dict(
        type=dict(query_factory=InventoryTransaction.type_filter),
    )

    form_extra_fields = {
        'total_amount': DisabledStringField(label=lazy_gettext('Total Amount')),
    }

    inline_models = (InventoryTransactionLineInlineAdmin(InventoryTransactionLine),)
