# coding=utf-8
from base import ModelViewWithAccess
from custom_fields import DisabledStringField
from enum_values import EnumValuesAdmin
from expense import ExpenseAdmin
from incoming import IncomingAdmin
from index import AdminIndexView
from preference import PreferenceAdmin
from product import ProductAdmin
from product_category import ProductCategoryAdmin
from purchase_order import PurchaseOrderAdmin
from sales_order import SalesOrderAdmin
from security import UserAdmin, RoleAdmin
from supplier import SupplierAdmin
from receiving import ReceivingAdmin
from shipping import ShippingAdmin
from inventory_transaction import InventoryTransactionAdmin
from product_inventory import ProductInventoryView
from customer import CustomerAdmin
from formatter import *
from app.models import *
from flask.ext.admin import Admin
from flask.ext.admin.consts import ICON_TYPE_GLYPH
from import_store_data import ImportStoreDataView


def init_admin_views(app, db):
    db_session = db.session
    admin_views = Admin(app, lazy_gettext('Brand Name'), index_view=AdminIndexView(),
                        base_template='layout.html', template_mode='bootstrap3')
    admin_views.add_view(PurchaseOrderAdmin(PurchaseOrder, db_session, name=lazy_gettext("Purchase Order"),
                                            category=lazy_gettext('Purchase'), menu_icon_type=ICON_TYPE_GLYPH,
                                            menu_icon_value='glyphicon-shopping-cart'))
    admin_views.add_view(ReceivingAdmin(Receiving, db_session, name=lazy_gettext("Receiving"),
                                        category=lazy_gettext('Purchase'), menu_icon_type=ICON_TYPE_GLYPH,
                                        menu_icon_value='glyphicon-import'))
    admin_views.add_view(SupplierAdmin(Supplier, db_session, name=lazy_gettext("Supplier"),
                                       category=lazy_gettext('Purchase'), menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-globe'))


    admin_views.add_view(SalesOrderAdmin(SalesOrder, db_session, name=lazy_gettext("Sales Order"),
                                         category=lazy_gettext('Sales'), menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-send'))
    admin_views.add_view(ShippingAdmin(Shipping, db_session, name=lazy_gettext("Shipping"),
                                       category=lazy_gettext('Sales'), menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-export'))
    admin_views.add_view(CustomerAdmin(Customer, db_session, name=lazy_gettext("Customer"),
                                       category=lazy_gettext('Sales'), menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-user'))
    admin_views.add_view(ProductInventoryView(Product, db_session, name=lazy_gettext("Operation Suggestion"),
                                              category=lazy_gettext('Sales'), menu_icon_type=ICON_TYPE_GLYPH,
                                              menu_icon_value='glyphicon-piggy-bank', endpoint='product_inventory'))

    admin_views.add_view(ExpenseAdmin(Expense, db_session, name=lazy_gettext("Expense"),
                                      category=lazy_gettext('Financial'), menu_icon_type=ICON_TYPE_GLYPH,
                                      menu_icon_value='glyphicon-minus-sign'))
    admin_views.add_view(IncomingAdmin(Incoming, db_session, name=lazy_gettext("Incoming"),
                                       category=lazy_gettext('Financial'), menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-usd'))

    admin_views.add_view(ProductAdmin(Product, db_session, name=lazy_gettext("Product"),
                                      category=lazy_gettext('Master Data'), menu_icon_type=ICON_TYPE_GLYPH,
                                      menu_icon_value='glyphicon-barcode'))
    admin_views.add_view(ProductCategoryAdmin(ProductCategory, db_session, name=lazy_gettext("Product Category"),
                                              category=lazy_gettext('Master Data'), menu_icon_type=ICON_TYPE_GLYPH,
                                              menu_icon_value='glyphicon-tags'))
    admin_views.add_view(InventoryTransactionAdmin(InventoryTransaction, db_session, name=lazy_gettext("Adjust Inventory"),
                                                   category=lazy_gettext('Master Data'), menu_icon_type=ICON_TYPE_GLYPH,
                                                   menu_icon_value='glyphicon-transfer'))
    admin_views.add_view(ImportStoreDataView(name=lazy_gettext("Import Store Data"), category=lazy_gettext('Master Data'),
                                             menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-shopping-cart',
                                             endpoint='import_store_data'))

    admin_views.add_view(UserAdmin(User, db_session, name=lazy_gettext('User'),
                                   category=lazy_gettext('Settings'), menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-user'))
    admin_views.add_view(RoleAdmin(Role, db_session, name=lazy_gettext("Role"),
                                   category=lazy_gettext('Settings'), menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-eye-close'))
    admin_views.add_view(EnumValuesAdmin(EnumValues, db_session, name=lazy_gettext("Enum Values"),
                                         category=lazy_gettext('Settings'), menu_icon_type=ICON_TYPE_GLYPH,
                                         menu_icon_value='glyphicon-tasks'))
    admin_views.add_view(PreferenceAdmin(Preference, db_session, name=lazy_gettext("Preference"),
                                         category=lazy_gettext('Settings'), menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-cog'))
    return admin_views
