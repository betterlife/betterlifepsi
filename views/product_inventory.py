from flask.ext.babelex import lazy_gettext
from views import ModelViewWithAccess, DisabledStringField
from formatter import supplier_formatter, product_formatter, available_quantity_formatter, default_decimal_formatter


class ProductInventoryView(ModelViewWithAccess):

    can_edit = False
    can_delete = False
    can_create = False

    column_list = ('name', 'supplier', 'available_quantity', 'in_transit_quantity',
                   'average_purchase_price', 'average_retail_price', 'average_unit_profit', 'weekly_sold_qty',
                   'weekly_average_profit', 'inventory_advice')

    column_searchable_list = ('name', 'supplier.name',)

    column_sortable_list = ('name', ('supplier', 'id'), 'available_quantity', 'in_transit_quantity',
                            'average_purchase_price', 'average_retail_price', 'average_unit_profit',)

    # column_filters = column_searchable_list
    column_labels = {
        'supplier.name': lazy_gettext('Supplier Name'),
        'supplier': lazy_gettext('Supplier'),
        'name': lazy_gettext('Product Name'),
        'available_quantity': lazy_gettext('Available Quantity'),
        'in_transit_quantity': lazy_gettext('In Transit Quantity'),
        'average_purchase_price': lazy_gettext('Average purchase price'),
        'average_retail_price': lazy_gettext('Average retail price'),
        'average_unit_profit': lazy_gettext('Average unit profit'),
        'weekly_sold_qty': lazy_gettext('Weekly sold quantity'),
        'weekly_average_profit': lazy_gettext('Weekly average profit'),
        'inventory_advice': lazy_gettext('Management advice')
    }

    column_formatters = {
        'supplier': supplier_formatter,
        'name': product_formatter,
        'available_quantity': available_quantity_formatter,
        'average_purchase_price': default_decimal_formatter,
        'average_retail_price': default_decimal_formatter,
        'average_unit_profit': default_decimal_formatter,
        'weekly_sold_qty': default_decimal_formatter,
        'weekly_average_profit': default_decimal_formatter
    }