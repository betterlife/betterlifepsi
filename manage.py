# coding=utf-8
from flask import Flask
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
# Run 'python manage.py db upgrade' to migrate DB.
app = Flask(__name__)

import config
app.config.from_object(config)

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app_provider import AppInfo
AppInfo.set_app(app)
AppInfo.set_db(db)
from models import PaymentMethod, Preference, Product, \
    ProductCategory, PurchaseOrder, PurchaseOrderLine, \
    EnumValues, Expense, SalesOrderLine, SalesOrder, \
    Supplier, Incoming
db.init_app(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()