from __future__ import print_function

import os

from psi.app import create_app, init_all
from psi.app.config import CITestConfig
from psi.app.service import Info


def init_app():
    from psi.app.config import TestConfig
    # warnings.warn("Recreating DB")
    # recreate_database(TestConfig)
    if os.environ.get('CI_MODE') == 'True':
        active_config = CITestConfig
    else:
        active_config = TestConfig
    application = create_app(active_config)
    init_all(application)
    return application


def recreate_database(config):
    import commands
    db_uri = config.SQLALCHEMY_DATABASE_URI
    db_name = db_uri[db_uri.rindex("/") + 1:]
    (s_d, o_d) = commands.getstatusoutput('psql -U postgres -c "DROP DATABASE {0}"'.format(db_name))
    print(s_d, o_d)
    (s_c, o_c) = commands.getstatusoutput('psql -U postgres -c "CREATE DATABASE {0}"'.format(db_name))
    print(s_c, o_c)


def login_as_admin(test_client):
    return login_user(test_client, 'support@betterlife.io', 'password')


def login_user(test_client, email, password):
    logout_user(test_client)
    return test_client.post('/login', data=dict(email_or_login=email, password=password), follow_redirects=True)


def run_as_user(test_client, email, password, func_to_run, *parameters):
    logout_user(test_client)
    with test_client:
        test_client.post('/login', data=dict(email_or_login=email, password=password), follow_redirects=True)
        func_to_run(*parameters)


def run_as_admin(test_client, func_to_run, *parameters):
    with test_client:
        login_as_admin(test_client)
        func_to_run(*parameters)


def logout_user(test_client):
    test_client.get('/logout', follow_redirects=True)


def cleanup_database(app_context):
    with app_context:
        db = Info.get_db()
        db.session.remove()
        db.engine.execute('DROP TABLE alembic_version')
        db.engine.execute('DROP VIEW sales_order_detail')
        db.session.commit()
        db.reflect()
        db.drop_all()
