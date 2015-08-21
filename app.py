# coding=utf-8
import shlex
import subprocess
from flask import Flask, redirect
from flask.ext.migrate import Migrate
from flask_security import SQLAlchemyUserDatastore, Security, login_required
import os

app = Flask(__name__)

import config

app.config.from_object(config)

from flask_babelex import Babel

babel = Babel(default_locale='zh_Hans_CN')
babel.init_app(app)

db = None


def init_db_security_admin():
    if db is None:
        from flask_sqlalchemy import SQLAlchemy
        v_db = SQLAlchemy(app)
        from app_provider import AppInfo
        AppInfo.set_app(app)
        AppInfo.set_db(v_db)
        from models import EnumValues, Expense, Incoming, InventoryTransaction, \
            InventoryTransactionLine, Preference, Product, ProductCategory, \
            PurchaseOrder, PurchaseOrderLine, Receiving, ReceivingLine, \
            SalesOrder, SalesOrderLine, User, Role, roles_users, Shipping, \
            ShippingLine, Supplier, PaymentMethod
        v_db.init_app(app)

        # Setup Flask-Security
        user_datastore = SQLAlchemyUserDatastore(v_db, User, Role)
        Security(app, user_datastore)

        from views import init_admin_views
        admin = init_admin_views(app, v_db)
        AppInfo.set_admin(admin)
        return v_db
    return db


if not app.config['TESTING']:
    db = init_db_security_admin()


@app.route('/')
def hello():
    return redirect("/admin", code=302)


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
    db.session.remove()


@babel.localeselector
def get_locale():
    # Put your logic here. Application can store locale in
    # user profile, cookie, session, etc.
    return 'zh_CN'
