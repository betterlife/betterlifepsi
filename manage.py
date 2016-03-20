#!/usr/bin/env python
# coding=utf-8
import nose
from flask import Flask
from flask.ext.migrate import Migrate, MigrateCommand
from raven.contrib.flask import Sentry
from flask.ext.script import Manager
from app.database import DbInfo


def init_app():
    app = Flask(__name__)
    return app


def init_db(flask_app):
    import app.config as config
    flask_app.config.from_object(config.BaseConfig)
    from flask.ext.sqlalchemy import SQLAlchemy
    db = SQLAlchemy(flask_app)
    DbInfo.set_db(db)
    from app.models import Customer, EnumValues, Expense, Incoming, InventoryTransaction, InventoryTransactionLine, \
        Preference, Product, ProductCategory, PurchaseOrder, PurchaseOrderLine, Receiving, ReceivingLine, \
        SalesOrder, SalesOrderLine, User, Role, Organization, Shipping, ShippingLine, Supplier, PaymentMethod
    db.init_app(flask_app)
    return db


def init_logger(app):
    # Init Sentry if not in debug mode
    if not app.config.get('DEBUG'):
        sentry = Sentry(app)


def init_manager(app):
    return Manager(app)


def init_migrate_command(m):
    migrate = Migrate(application, database)
    m.add_command('db', MigrateCommand)


# 'python manage.py db migrate'
#   - generate migration script from current schema version.
# 'python manage.py db upgrade'
#   - migrate DB.
application = init_app()
database = init_db(application)
init_logger(application)
manager = init_manager(application)
init_migrate_command(manager)


@manager.command
def test():
    """Run the unit tests.
    "" python manage.py test
    """
    import subprocess
    subprocess.call('nosetests -w tests --with-coverage --cover-erase --with-xunit --cover-branches --xunit-file=nosetests.xml',
                    shell=True)


@application.teardown_appcontext
def shutdown_session(exception=None):
    database.session.remove()


if __name__ == '__main__':
    manager.run()
