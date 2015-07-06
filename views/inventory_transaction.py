from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext
from models import InventoryTransactionLine, InventoryTransaction
from views import ModelViewWithAccess, ReadOnlyStringField


class InventoryTransactionLineInlineAdmin(InlineFormAdmin):

    form_args = dict(
        id=dict(label=lazy_gettext('Id')),
        product=dict(label=lazy_gettext('Product')),
        price=dict(label=lazy_gettext('Inventory Transaction Price')),
        quantity=dict(label=lazy_gettext('Quantity')),
        remark=dict(label=lazy_gettext('Remark')),
    )

    def postprocess_form(self, form):
        form.total_amount = ReadOnlyStringField(label=lazy_gettext('Total Amount'))
        return form

class InventoryTransactionAdmin(ModelViewWithAccess):
    column_list = ('id', 'type', 'date', 'total_amount', 'remark')

    column_labels = {
        'id': lazy_gettext('Id'),
        'type': lazy_gettext('Inventory Transaction Type'),
        'date': lazy_gettext('Date'),
        'total_amount': lazy_gettext('Total Amount'),
        'remark': lazy_gettext('Remark'),
        'lines': lazy_gettext('Lines')
    }

    form_args = dict(
        type=dict(query_factory=InventoryTransaction.type_filter),
    )

    form_extra_fields = {
        'total_amount': ReadOnlyStringField(label=lazy_gettext('Total Amount')),
    }

    inline_models = (InventoryTransactionLineInlineAdmin(InventoryTransactionLine),)

    pass
