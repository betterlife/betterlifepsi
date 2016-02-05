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
from formatter import *
from app.models import *
from flask.ext.admin import Admin
from flask.ext.admin.consts import ICON_TYPE_GLYPH
from import_store_data import ImportStoreDataView


def init_admin_views(app, db):
    db_session = db.session
    adminViews = Admin(app, lazy_gettext('Brand Name'), index_view=AdminIndexView(),
                       base_template='layout.html', template_mode='bootstrap3')
    adminViews.add_view(PurchaseOrderAdmin(PurchaseOrder, db_session, name=lazy_gettext("Purchase Order"),
                                           category=u'订单', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-shopping-cart'))
    adminViews.add_view(SalesOrderAdmin(SalesOrder, db_session, name=lazy_gettext("Sales Order"),
                                        category=u'订单', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-send'))
    adminViews.add_view(ReceivingAdmin(Receiving, db_session, name=lazy_gettext("Receiving"),
                                       category=u'库存', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-import'))
    adminViews.add_view(ShippingAdmin(Shipping, db_session, name=lazy_gettext("Shipping"),
                                      category=u'库存', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-export'))
    adminViews.add_view(InventoryTransactionAdmin(InventoryTransaction, db_session, name=lazy_gettext("Inventory Transaction"),
                                                  category=u'库存', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-transfer'))
    adminViews.add_view(ProductInventoryView(Product, db_session, name=lazy_gettext("Product Inventory"),
                                             category=u'库存', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-piggy-bank',
                                             endpoint='product_inventory'))
    adminViews.add_view(ExpenseAdmin(Expense, db_session, name=lazy_gettext("Expense"),
                                     category=u'财务', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-minus-sign'))
    adminViews.add_view(IncomingAdmin(Incoming, db_session, name=lazy_gettext("Incoming"),
                                      category=u'财务', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-usd'))
    adminViews.add_view(SupplierAdmin(Supplier, db_session, name=lazy_gettext("Supplier"),
                                      category=u'主数据', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-user'))
    adminViews.add_view(ProductAdmin(Product, db_session, name=lazy_gettext("Product"),
                                     category=u'主数据', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-barcode'))
    adminViews.add_view(ProductCategoryAdmin(ProductCategory, db_session, name=lazy_gettext("Product Category"),
                                             category=u'主数据', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tags'))
    adminViews.add_view(ImportStoreDataView(name=lazy_gettext("Import Store Data"), category=u'数据维护',
                                            menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-shopping-cart',
                                            endpoint='import_store_data'))
    adminViews.add_view(EnumValuesAdmin(EnumValues, db_session, name=lazy_gettext("Enum Values"),
                                        category=u'设置', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tasks'))
    adminViews.add_view(PreferenceAdmin(Preference, db_session, name=lazy_gettext("Preference"),
                                        category=u'设置', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-cog'))
    adminViews.add_view(UserAdmin(User, db_session, name=lazy_gettext('User'),
                                  category=u'安全', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-user'))
    adminViews.add_view(RoleAdmin(Role, db_session, name=lazy_gettext("Role"),
                                  category=u'安全', menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-eye-close'))
    return adminViews
