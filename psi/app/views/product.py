# coding=utf-8
from psi.app.models.product import ProductImage
from psi.app.utils import form_util, security_util
from psi.app.views.components import ImageField, images_formatter
from flask_babelex import lazy_gettext

from psi.app.views.base import ModelViewWithAccess


class ProductAdmin(ModelViewWithAccess):
    from psi.app.views.formatter import supplier_formatter, rich_text_formatter
    from psi.app.views.components.string_fields import DisabledStringField, CKTextAreaField, \
        ReadonlyStringField

    # inline_models = (ProductImagesAdmin(ProductImage),)

    column_editable_list = ['name', 'deliver_day', 'lead_day', 'spec_link',
                            'purchase_price', 'retail_price']
    column_searchable_list = ['name', 'supplier.name', 'category.name', 'mnemonic']

    column_sortable_list = ('id', 'name', ('supplier', 'supplier.id'),
                            ('category','category.id'), 'deliver_day', 'lead_day',
                            'purchase_price', 'retail_price',
                            'available_quantity', 'in_transit_quantity',)

    column_filters = column_searchable_list
    column_labels = {
        'id': lazy_gettext('id'),
        'supplier.name': lazy_gettext('Supplier Name'),
        'category.name': lazy_gettext('CategoryName'),
        'category.code': lazy_gettext('Category Code'),
        'supplier': lazy_gettext('Supplier'),
        'name': lazy_gettext('Name'),
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
        'external_id': lazy_gettext('External Id'),
        'images_placeholder': lazy_gettext('Product Images'),
    }

    form_extra_fields = {
        'available_quantity': DisabledStringField(label=lazy_gettext('Available Quantity')),
        'in_transit_quantity': DisabledStringField(label=lazy_gettext('In Transit Quantity')),
        'images_placeholder': ImageField(label=lazy_gettext('Product Images')),
        'gross_profit_rate': DisabledStringField(label=lazy_gettext('Gross Profit Rate')),
    }

    column_formatters = {
        'supplier': supplier_formatter,
        'distinguishing_feature': rich_text_formatter,
        'images_placeholder': images_formatter,
    }

    form_overrides = dict(distinguishing_feature=CKTextAreaField,
                          external_id=ReadonlyStringField)

    form_args = dict(
        distinguishing_feature=dict(description=lazy_gettext('Distinguishing feature of this product, useful for '
                                                             'introduce the product to our customer')),
        deliver_day=dict(description=lazy_gettext('Days for the product from shipped to arrive the store')),
        lead_day=dict(description=lazy_gettext('Days from the day we contact supplier to the day they begin to '
                                               'ship product')),
        need_advice=dict(description=lazy_gettext('Need running advice for this product?')),
    )

    column_list = ('id', 'name', 'supplier', 'category', 'lead_day',
                   'deliver_day', 'purchase_price', 'retail_price', 'gross_profit_rate',
                   'available_quantity', 'in_transit_quantity',)

    form_columns = ('name', 'category', 'supplier', 'lead_day',
                    'deliver_day', 'purchase_price', 'retail_price', 'gross_profit_rate',
                    'available_quantity', 'in_transit_quantity',
                    'spec_link', 'need_advice', 'images_placeholder',
                    'distinguishing_feature',)

    form_create_rules = (
        'name', 'category', 'supplier', 'lead_day', 'deliver_day',
        'purchase_price', 'retail_price', 'spec_link', 'images_placeholder',
        'distinguishing_feature',
    )

    column_details_list = ('id', 'external_id', 'name', 'category',
                           'supplier', 'lead_day', 'deliver_day',
                           'purchase_price', 'retail_price', 'gross_profit_rate',
                           'available_quantity', 'in_transit_quantity',
                           'spec_link', 'need_advice', 'images_placeholder',
                           'distinguishing_feature',)

    def create_form(self, obj=None):
        from psi.app.models import ProductCategory, Supplier
        form = super(ProductAdmin, self).create_form(obj)
        form.images_placeholder.set_object_type(ProductImage)
        form_util.filter_by_organization(form.category, ProductCategory)
        form_util.filter_by_organization(form.supplier, Supplier)
        return form

    def edit_form(self, obj=None):
        from psi.app.models import ProductCategory, Supplier
        form = super(ProductAdmin, self).edit_form(obj)
        form.images_placeholder.set_object_type(ProductImage)
        form_util.filter_by_organization(form.category, ProductCategory)
        form_util.filter_by_organization(form.supplier, Supplier)
        if not security_util.user_has_role('purchase_price_view'):
            form_util.del_form_field(self, form, 'purchase_price')
        return form

    def get_details_columns(self):
        columns = super(ProductAdmin, self).get_details_columns()
        columns = security_util.filter_columns_by_role(columns, ['purchase_price'],
                                                       'purchase_price_view')
        return columns

    def get_list_columns(self):
        """
        This method is called instantly in list.html
        List of columns is decided runtime during render of the table
        Not decided during flask-admin blueprint startup(which is the default
        behavior of flask-admin).
        """
        columns = super(ProductAdmin, self).get_list_columns()
        columns = security_util.filter_columns_by_role(columns, ['purchase_price'],
                                                       'purchase_price_view')
        return columns
