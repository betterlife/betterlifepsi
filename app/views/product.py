# coding=utf-8
from flask.ext.babelex import lazy_gettext
from app.models.product import Product
from app.views.formatter import supplier_formatter
from app.views.base import ModelViewWithAccess
from app.views.custom_fields import DisabledStringField, CKTextAreaField, ReadonlyStringField


class ProductAdmin(ModelViewWithAccess):
    column_editable_list = ['name', 'deliver_day', 'lead_day', 'distinguishing_feature',
                            'spec_link', 'purchase_price', 'retail_price']
    column_searchable_list = ['code', 'name', 'supplier.name', 'category.name', 'category.code']

    column_sortable_list = ('id', 'code', 'name', ('supplier', 'id'), ('category', 'code'),
                            'deliver_day', 'lead_day', 'purchase_price', 'retail_price',
                            'available_quantity', 'in_transit_quantity',)

    column_filters = column_searchable_list
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
        'need_advice': lazy_gettext('Need Running Advice'),
    }

    form_extra_fields = {
        'available_quantity': DisabledStringField(label=lazy_gettext('Available Quantity')),
        'in_transit_quantity': DisabledStringField(label=lazy_gettext('In Transit Quantity')),
    }

    column_formatters = {
        'supplier': supplier_formatter
    }

    form_overrides = dict(distinguishing_feature=CKTextAreaField, code=ReadonlyStringField)

    form_args = dict(
        distinguishing_feature=dict(description=lazy_gettext('Distinguishing feature of this product, useful for '
                                                             'introduce the product to our customer')),
        deliver_day=dict(description=lazy_gettext('Days for the product from shipped to arrive the store')),
        lead_day=dict(description=lazy_gettext('Days from the day we contact supplier to the day they begin to '
                                               'ship product')),
        code=dict(description=lazy_gettext('Product code is generated automatically')),
        need_advice=dict(description=lazy_gettext('Need running advice for this product?'))
    )

    column_list = ('id', 'supplier', 'category', 'code', 'name', 'lead_day', 'deliver_day', 'purchase_price',
                   'retail_price', 'available_quantity', 'in_transit_quantity',)

    form_columns = ('category', 'supplier', 'code', 'name', 'lead_day', 'deliver_day', 'purchase_price',
                    'retail_price', 'available_quantity', 'in_transit_quantity', 'spec_link', 'need_advice',
                    'distinguishing_feature',)

    form_create_rules = (
        'category', 'supplier', 'code', 'name', 'lead_day', 'deliver_day',
        'purchase_price', 'retail_price', 'spec_link', 'distinguishing_feature',
    )

    def create_form(self, obj=None):
        form = super(ModelViewWithAccess, self).create_form(obj)
        form.code.data = Product.get_next_code()
        return form
