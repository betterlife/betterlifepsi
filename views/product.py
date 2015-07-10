# coding=utf-8
from flask.ext.babelex import lazy_gettext
from views.base import ModelViewWithAccess
from views.custom_fields import  DisabledStringField


class ProductAdmin(ModelViewWithAccess):
    column_editable_list = ['name', 'deliver_day', 'lead_day', 'distinguishing_feature',
                            'spec_link', 'purchase_price', 'retail_price']
    column_searchable_list = ('code', 'name', 'supplier.name', 'category.name', 'category.code')

    column_sortable_list = ('id', 'code', 'name', ('supplier', 'id'), ('category', 'code'),
                            'deliver_day', 'lead_day', 'purchase_price', 'retail_price',
                            'available_quantity', 'in_transit_quantity',)

    # column_filters = column_searchable_list
    column_labels = {
        'id': lazy_gettext('id'),
        'supplier.name': lazy_gettext('Supplier Name'),
        'category.name': lazy_gettext('Category Name'),
        'category.code': lazy_gettext('Category Code'),
        'supplier': lazy_gettext('Supplier'),
        'name': lazy_gettext('Name'),
        'code': lazy_gettext('Code'),
        'category': lazy_gettext('Category'),
        'deliver_day': lazy_gettext('Deliver Day'),
        'lead_day': lazy_gettext('Lead Day'),
        'distinguishing_feature': lazy_gettext('Distinguishing Feature'),
        'spec_link': lazy_gettext('Spec Link'),
        'purchase_price': lazy_gettext('Purchase Price'),
        'retail_price': lazy_gettext('Retail Price'),
        'available_quantity': lazy_gettext('Available Quantity'),
        'in_transit_quantity': lazy_gettext('In Transit Quantity'),
    }

    form_extra_fields = {
        'available_quantity': DisabledStringField(label=lazy_gettext('Available Quantity')),
        'in_transit_quantity': DisabledStringField(label=lazy_gettext('In Transit Quantity')),
    }

    column_list = ('id', 'supplier', 'category', 'code', 'name', 'deliver_day', 'lead_day', 'purchase_price',
                   'retail_price', 'available_quantity', 'in_transit_quantity')

    form_columns = ('category', 'supplier', 'code', 'name', 'deliver_day', 'lead_day', 'distinguishing_feature',
                    'spec_link', 'purchase_price', 'retail_price', 'available_quantity', 'in_transit_quantity',)