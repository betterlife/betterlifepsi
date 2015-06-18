# coding=utf-8
from flask.ext.admin import Admin
from flask.ext.admin.consts import ICON_TYPE_GLYPH
from models import *
from views import *
from database import db_session

def init_admin_views(app):
    admin = Admin(app, u'管理后台', base_template='layout.html', template_mode='bootstrap3')
    admin.add_view(ProductAdmin(Product, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-barcode'))
    admin.add_view(SupplierAdmin(Supplier, db_session,  menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-globe'))
    admin.add_view(PurchaseOrderAdmin(PurchaseOrder, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-shopping-cart'))
    admin.add_view(SalesOrderAdmin(SalesOrder, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-send'))
    admin.add_view(ExpenseAdmin(Expense, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-usd'))
    admin.add_view(IncomingAdmin(Incoming, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-minus-sign'))
    admin.add_view(EnumValuesAdmin(EnumValues, db_session, category='Settings', name='基础分类',
                                   menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tasks'))
    admin.add_view(ProductCategoryAdmin(ProductCategory, db_session, category='Settings', name='产品分类',
                                        menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tags'))
    return admin



