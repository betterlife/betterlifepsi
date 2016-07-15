#!/usr/bin/env python
# coding=utf-8

import sys

reload(sys)
sys.setdefaultencoding("utf-8")


def init_app():
    from flask import Flask

    app = Flask(__name__)
    return app


def init_db(flask_app):
    import app.config as config
    from app.service import Info

    flask_app.config.from_object(config.BaseConfig)
    from flask.ext.sqlalchemy import SQLAlchemy
    db = SQLAlchemy(flask_app)
    Info.set_db(db)
    from app.models import Customer, EnumValues, Expense, Incoming, InventoryTransaction, InventoryTransactionLine
    from app.models import Preference, Product, ProductCategory, PurchaseOrder, PurchaseOrderLine, Receiving, ReceivingLine
    from app.models import SalesOrder, SalesOrderLine, User, Role, Organization, Shipping, ShippingLine, Supplier, PaymentMethod
    db.init_app(flask_app)
    return db


def init_logger(app):
    # Init Sentry if not in debug mode
    from raven.contrib.flask import Sentry

    if not app.config.get('DEBUG'):
        Sentry(app)


def init_manager(app):
    from flask.ext.script import Manager

    return Manager(app)


def init_migrate_command(m):
    from flask.ext.migrate import Migrate, MigrateCommand

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
