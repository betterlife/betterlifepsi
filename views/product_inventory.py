from flask.ext.babelex import lazy_gettext
from views import ModelViewWithAccess, DisabledStringField
from formatter import supplier_formatter


class ProductInventoryView(ModelViewWithAccess):

    can_edit = False
    can_delete = False
    can_create = False

    column_list = ('code', 'name', 'supplier', 'category', 'lead_day', 'deliver_day',
                   'available_quantity', 'in_transit_quantity',)

    column_searchable_list = ('code', 'name', 'supplier.name', 'category.name', 'category.code')

    column_sortable_list = ('code', 'name', ('supplier', 'id'), ('category', 'code'),
                            'deliver_day', 'lead_day', 'available_quantity', 'in_transit_quantity',)

    # column_filters = column_searchable_list
    column_labels = {
        'supplier.name': lazy_gettext('Supplier Name'),
        'category.name': lazy_gettext('Category Name'),
        'category.code': lazy_gettext('Category Code'),
        'supplier': lazy_gettext('Supplier'),
        'name': lazy_gettext('Name'),
        'code': lazy_gettext('Code'),
        'category': lazy_gettext('Category'),
        'deliver_day': lazy_gettext('Deliver Day'),
        'lead_day': lazy_gettext('Lead Day'),
        'available_quantity': lazy_gettext('Available Quantity'),
        'in_transit_quantity': lazy_gettext('In Transit Quantity'),
    }

    form_extra_fields = {
        'available_quantity': DisabledStringField(label=lazy_gettext('Available Quantity')),
        'in_transit_quantity': DisabledStringField(label=lazy_gettext('In Transit Quantity')),
    }

    column_formatters = {
        'supplier': supplier_formatter
    }