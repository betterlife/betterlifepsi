# coding=utf-8
from psi.app.models.product_inventory import ProductInventory
from psi.app.models.supplier_sales import OverallSupplierSales
from psi.app.models.product_sales import OverallProductSales
from psi.app.views.supplier_sales_report import SupplierSalesReportAdmin
from psi.app.views.product_sales_report import ProductSalesReportAdmin 
from psi.app.models import *
from psi.app.models.organization import Organization
from flask_admin import Admin
from flask_admin.consts import ICON_TYPE_GLYPH

from .base import ModelViewWithAccess
from .enum_values import EnumValuesAdmin
from .expense import ExpenseAdmin
from .incoming import IncomingAdmin
from .index import AdminIndexView
from .preference import PreferenceAdmin
from .product import ProductAdmin
from .product_category import ProductCategoryAdmin
from .sales_order import SalesOrderAdmin
from .user import UserAdmin
from .role import RoleAdmin
from .organization import OrganizationAdmin
from .supplier import SupplierAdmin
from .receiving import ReceivingAdmin
from .shipping import ShippingAdmin
from .inventory_transaction import InventoryTransactionAdmin
from .product_inventory import ProductInventoryView
from .customer import CustomerAdmin
from .formatter import *
from .import_store_data import ImportStoreDataView
from .report import ReportView
from .direct_purchase_order import DirectPurchaseOrderAdmin
from .franchise_purchase_order import FranchisePurchaseOrderAdmin


def init_admin_views(app, db):
    db_session = db.session
    admin_views = Admin(
        app, lazy_gettext('Betterlife'),
        index_view=AdminIndexView(),
        base_template='layout.html',
        template_mode='bootstrap3'
    )
    admin_views.add_view(DirectPurchaseOrderAdmin(
        PurchaseOrder,
        db_session,
        name=lazy_gettext("Direct Purchase Order"),
        category=lazy_gettext('Purchase'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-shopping-cart',
        endpoint='dpo')
    )
    admin_views.add_view(FranchisePurchaseOrderAdmin(
        PurchaseOrder,
        db_session,
        name=lazy_gettext("Franchise Purchase Order"),
        category=lazy_gettext('Purchase'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-shopping-cart',
        endpoint='fpo')
    )
    admin_views.add_view(ReceivingAdmin(
        Receiving,
        db_session,
        name=lazy_gettext("Receiving"),
        category=lazy_gettext('Purchase'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-import')
    )
    admin_views.add_view(SupplierAdmin(
        Supplier,
        db_session,
        name=lazy_gettext("Supplier"),
        category=lazy_gettext('Purchase'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-globe')
    )

    admin_views.add_view(SalesOrderAdmin(
        SalesOrder,
        db_session,
        name=lazy_gettext("Sales Order"),
        category=lazy_gettext('Sales'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-send')
    )
    admin_views.add_view(ShippingAdmin(
        Shipping,
        db_session,
        name=lazy_gettext("Shipping"),
        category=lazy_gettext('Sales'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-export')
    )
    admin_views.add_view(CustomerAdmin(
        Customer,
        db_session,
        name=lazy_gettext("Customer"),
        category=lazy_gettext('Sales'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-user')
    )
    admin_views.add_view(ProductInventoryView(
        ProductInventory,
        db_session,
        name=lazy_gettext("Operation Suggestion"),
        category=lazy_gettext('Sales'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-piggy-bank',
        endpoint='product_inventory')
    )
    admin_views.add_view(ExpenseAdmin(
        Expense,
        db_session,
        name=lazy_gettext("Expense"),
        category=lazy_gettext('Financial'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-minus-sign')
    )
    admin_views.add_view(IncomingAdmin(
        Incoming,
        db_session,
        name=lazy_gettext("Incoming"),
        category=lazy_gettext('Financial'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-usd')
    )

    admin_views.add_view(ProductAdmin(
        Product,
        db_session,
        name=lazy_gettext("Product"),
        category=lazy_gettext('Master Data'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-barcode')
    )
    admin_views.add_view(ProductCategoryAdmin(
        ProductCategory,
        db_session,
        name=lazy_gettext("Product Category"),
        category=lazy_gettext('Master Data'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-tags')
    )
    admin_views.add_view(InventoryTransactionAdmin(
        InventoryTransaction,
        db_session,
        name=lazy_gettext("Adjust Inventory"),
        category=lazy_gettext('Master Data'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-transfer')
    )
    admin_views.add_view(ImportStoreDataView(
        name=lazy_gettext("Import Store Data"),
        category=lazy_gettext('Master Data'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-shopping-cart',
        endpoint='import_store_data')
    )
    admin_views.add_view(ReportView(
        name=lazy_gettext('Sales Amount Report'),
        category=lazy_gettext("Report"),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='fa fa-bar-chart',
        endpoint='sales_amount',
        url="report/sales_amount")
    )
    admin_views.add_view(ReportView(
        name=lazy_gettext('Sales Profit Report'),
        category=lazy_gettext("Report"),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='fa fa-bar-chart',
        endpoint='sales_profit',
        url="report/sales_profit"),
    )
    admin_views.add_view(SupplierSalesReportAdmin(
        OverallSupplierSales,
        db_session,
        name=lazy_gettext("Supplier Sales Report"),
        category=lazy_gettext('Report'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='fa fa-bar-chart',
        endpoint='supplier_sales_report')
    )
    admin_views.add_view(ProductSalesReportAdmin(
        OverallProductSales,
        db_session,
        name=lazy_gettext("Product Sales Report"),
        category=lazy_gettext('Report'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='fa fa-bar-chart',
        endpoint='product_sales_report')
    )
    admin_views.add_view(UserAdmin(
        User,
        db_session,
        name=lazy_gettext('User'),
        category=lazy_gettext('Settings'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-user')
    )
    admin_views.add_view(RoleAdmin(
        Role,
        db_session,
        name=lazy_gettext("Role"),
        category=lazy_gettext('Settings'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-eye-close')
    )
    admin_views.add_view(OrganizationAdmin(
        Organization,
        db_session,
        name=lazy_gettext("Organization"),
        category=lazy_gettext('Settings'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-user')
    )
    admin_views.add_view(EnumValuesAdmin(
        EnumValues,
        db_session,
        name=lazy_gettext("Enum Values"),
        category=lazy_gettext('Settings'),
        menu_icon_type=ICON_TYPE_GLYPH,
        menu_icon_value='glyphicon-tasks')
    )
    return admin_views
