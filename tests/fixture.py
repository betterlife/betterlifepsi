from app import create_app, init_all
from app.service import Info


def init_app():
    from app.config import TestConfig
    application = create_app(TestConfig)
    init_all(application)
    return application


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


def cleanup_database(app_context):
    with app_context:
        Info.get_db().session.remove()
        Info.get_db().engine.execute('DROP TABLE alembic_version')
        Info.get_db().engine.execute('DROP VIEW sales_order_detail')
        Info.get_db().session.commit()
        Info.get_db().drop_all()
