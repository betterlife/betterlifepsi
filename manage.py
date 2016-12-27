#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
import sys

from app.service import Info
from app import create_app, init_all

reload(sys)
sys.setdefaultencoding("utf-8")


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
application = create_app()
init_all(application)
database = Info.get_db()
manager = init_manager(application)
init_migrate_command(manager)


@manager.command
def test():
    """Run the unit tests.
    "" python manage.py test
    """
    import subprocess
    subprocess.call('nosetests -w tests --with-coverage --cover-erase --with-xunit --cover-branches --xunit-file=nosetests.xml', shell=True)


@manager.command
def generate_fake_order():
    """
    Load a set of fake data to the system
    * 10 Suppliers and customers
    * 5 purchase orders and sales_orders
    """
    from tests.object_faker import object_faker
    from app.models import User
    from random import randint
    user = database.session.query(User).get(1)
    for i in range(5):
        purchase_order = object_faker.purchase_order(creator=user, number_of_line=randint(1,9))
        sales_order = object_faker.sales_order(creator=user, number_of_line=randint(1, 9))
        database.session.add(purchase_order, sales_order)
    database.session.commit()

@application.teardown_appcontext
def shutdown_session(exception=None):
    database.session.remove()

if __name__ == '__main__':
    manager.run()
