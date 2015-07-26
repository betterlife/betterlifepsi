from flask.ext.babelex import lazy_gettext
from views import ModelViewWithAccess, DisabledStringField
from formatter import supplier_formatter, product_formatter, available_quantity_formatter


class ProductInventoryView(ModelViewWithAccess):

    can_edit = False
    can_delete = False
    can_create = False

    column_list = ('name', 'supplier', 'lead_day', 'deliver_day',
                   'available_quantity', 'in_transit_quantity', 'average_purchase_price', 'average_retail_price')

    column_searchable_list = ('name', 'supplier.name',)

    column_sortable_list = ('name', ('supplier', 'id'), 'deliver_day', 'lead_day', 'available_quantity',
                            'in_transit_quantity', 'average_purchase_price', 'average_retail_price')

    # column_filters = column_searchable_list
    column_labels = {
        'supplier.name': lazy_gettext('Supplier Name'),
        'supplier': lazy_gettext('Supplier'),
        'name': lazy_gettext('Name'),
        'deliver_day': lazy_gettext('Deliver Day'),
        'lead_day': lazy_gettext('Lead Day'),
        'available_quantity': lazy_gettext('Available Quantity'),
        'in_transit_quantity': lazy_gettext('In Transit Quantity'),
        'average_purchase_price': lazy_gettext('Average purchase price'),
        'average_retail_price': lazy_gettext('Average retail price'),
    }

    column_formatters = {
        'supplier': supplier_formatter,
        'name': product_formatter,
        'available_quantity': available_quantity_formatter,
    }