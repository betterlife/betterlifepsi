import time

from psi.app.models import Product
from flask_admin.contrib.sqla.filters import FloatSmallerFilter, FloatGreaterFilter
from flask_babelex import lazy_gettext

from psi.app.views.base import ModelViewWithAccess


class ProductInventoryView(ModelViewWithAccess):
    from .formatter import supplier_formatter, product_formatter, available_quantity_formatter, default_decimal_formatter
    can_edit = False
    can_delete = False
    can_create = False
    can_view_details = False

    @property
    def role_identify(self): return "product_inventory"

    column_list = ('name', 'available_quantity', 'in_transit_quantity',
                   'average_purchase_price', 'average_retail_price', 'average_unit_profit', 'weekly_sold_qty',
                   'weekly_average_profit', 'inventory_advice')

    column_searchable_list = ('name', 'supplier.name', 'mnemonic', 'supplier.mnemonic')

    column_filters = (FloatSmallerFilter(Product.available_quantity, lazy_gettext('Available Quantity')),
                      FloatGreaterFilter(Product.available_quantity, lazy_gettext('Available Quantity')),
                      FloatGreaterFilter(Product.in_transit_quantity, lazy_gettext('In Transit Quantity')),)

    column_sortable_list = ('name', 'available_quantity', 'in_transit_quantity', 'average_purchase_price',
                            'average_retail_price', 'average_unit_profit',)

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

    def get_query(self):
        self.update_need_advice_flag()
        return super(ProductInventoryView, self).get_query().filter(self.model.need_advice == True)

    def update_need_advice_flag(self):
        def get_time_in_second(key):
            return int(time.time())
        from psi.app.service import Info
        from psi.app.models import ProductInventory
        from flask import current_app
        last_update = Info.get('need_advice_last_update_timestamp', get_time_in_second)
        if int((time.time() - last_update)) > current_app.config['NEED_ADVICE_UPDATE_SECONDS']:
            session = Info.get_db().session
            all_products = Product.query.all()
            for p in all_products:
                p.need_advice = False
                session.add(p)
            products = ProductInventory.query.order_by(ProductInventory.weekly_average_profit).limit(50).all()
            for p in products:
                p.need_advice = True
                session.add(p)
            session.commit()

    def get_count_query(self):
        return super(ProductInventoryView, self).get_count_query().filter(self.model.need_advice == True)
