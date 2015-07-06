from base import ModelViewWithAccess
from custom_fields import ReadOnlyStringField
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
from flask.ext.babelex import lazy_gettext
from models import *
from flask.ext.admin import Admin
from flask.ext.admin.consts import ICON_TYPE_GLYPH
from views.inventory_transaction import InventoryTransactionAdmin


def init_admin_views(app, db):
    db_session = db.session
    adminViews = Admin(app, lazy_gettext('Brand Name'), index_view=AdminIndexView(),
                       base_template='layout.html', template_mode='bootstrap3')
    adminViews.add_view(PurchaseOrderAdmin(PurchaseOrder, db_session, name=lazy_gettext("Purchase Order"),
                                           category='Order', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-shopping-cart'))
    adminViews.add_view(SalesOrderAdmin(SalesOrder, db_session, name=lazy_gettext("Sales Order"),
                                        category='Order', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-send'))
    adminViews.add_view(ExpenseAdmin(Expense, db_session, name=lazy_gettext("Expense"),
                                     category='Financial', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-minus-sign'))
    adminViews.add_view(IncomingAdmin(Incoming, db_session, name=lazy_gettext("Incoming"),
                                      category='Financial', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-usd'))
    adminViews.add_view(SupplierAdmin(Supplier, db_session, name=lazy_gettext("Supplier"),
                                      category='Master Data', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-user'))
    adminViews.add_view(ProductAdmin(Product, db_session, name=lazy_gettext("Product"),
                                     category='Master Data', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-barcode'))
    adminViews.add_view(ProductCategoryAdmin(ProductCategory, db_session, name=lazy_gettext("Product Category"),
                                             category='Master Data', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tags'))
    adminViews.add_view(EnumValuesAdmin(EnumValues, db_session, name=lazy_gettext("Enum Values"),
                                        category='Settings', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tasks'))
    adminViews.add_view(PreferenceAdmin(Preference, db_session, name=lazy_gettext("Preference"),
                                        category='Settings', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-cog'))
    adminViews.add_view(UserAdmin(User, db_session, name=lazy_gettext('User'),
                                  category='Security', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-user'))
    adminViews.add_view(RoleAdmin(Role, db_session, name=lazy_gettext("Role"),
                                  category='Security', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-eye-close'))
    adminViews.add_view(InventoryTransactionAdmin(InventoryTransaction, db_session, name=lazy_gettext("Inventory"),
                                                  menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-transfer'))
    return adminViews