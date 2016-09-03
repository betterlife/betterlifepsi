from __future__ import print_function
from app import create_app, init_all
from app.service import Info


def init_app():
    from app.config import TestConfig
    # recreate_database(TestConfig)
    application = create_app(TestConfig)
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
    return test_client.post('/login', data=dict(email=email,
                                                password=password),
                            follow_redirects=True)


def run_test_as_admin(test_client, func_to_run, *parameters):
    with test_client:
        login_as_admin(test_client)
        func_to_run(*parameters)


def logout_user(test_client):
    test_client.get('/logout', follow_redirects=True)


def cleanup_database(app_context):
    with app_context:
        Info.get_db().session.remove()
        Info.get_db().engine.execute('DROP TABLE alembic_version')
        Info.get_db().engine.execute('DROP VIEW sales_order_detail')
        Info.get_db().session.commit()
        Info.get_db().drop_all()
