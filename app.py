# coding=utf-8
from database import init_database
from flask import Flask, request, session
from flask.ext.admin import Admin
from flask.ext.admin.consts import ICON_TYPE_GLYPH
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.babelex import Babel

# configuration
from models import *
from views import *

DEBUG = True
SECRET_KEY = 'development key'
BABEL_DEFAULT_LOCALE = 'zh_CN'
BABEL_DEFAULT_TIMEZONE = 'CST'

app = Flask(__name__)
app.config.from_object(__name__)
db_session = init_database()
# babel = init_i18n(app)
babel = Babel(app, default_locale="zh_CN", default_timezone="CST")

admin = Admin(app, u'管理后台', base_template='layout.html', template_mode='bootstrap3')
admin.add_view(ProductAdmin(Product, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-barcode'))
admin.add_view(SupplierAdmin(Supplier, db_session,  menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-globe'))
admin.add_view(PurchaseOrderAdmin(PurchaseOrder, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-shopping-cart'))
admin.add_view(SalesOrderAdmin(SalesOrder, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-send'))
admin.add_view(ExpenseAdmin(Expense, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-usd'))
admin.add_view(ModelView(Incoming, db_session, menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-minus-sign'))
admin.add_view(EnumValuesAdmin(EnumValues, db_session, category='Settings', name='基础分类',
                               menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tasks'))
admin.add_view(ProductCategoryAdmin(ProductCategory, db_session, category='Settings', name='产品分类',
                                    menu_icon_type=ICON_TYPE_GLYPH, menu_icon_value='glyphicon-tags'))


@babel.localeselector
def get_locale():
    override = request.args.get('lang')
    if override:
        session['lang'] = override
    lang = session.get('lang', 'zh_CN')
    print lang
    return lang

if __name__ == '__main__':
    app.run()

@app.before_request
def before_request():
    pass


@app.teardown_request
def teardown_request(exception):
    pass


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()