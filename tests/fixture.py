import os

from alembic import context

from app.database import DbInfo
from app import create_app, init_all


def init_app():
    from app.config import TestConfig
    application = create_app(TestConfig)
    init_all(application)
    return application


def login_as_admin(test_client):
    return test_client.post('/login', data=dict(email='support@betterlife.io', password='password'), follow_redirects=True)


def cleanup_database(app_context):
    with app_context:
        DbInfo.get_db().session.remove()
        DbInfo.get_db().engine.execute('DROP TABLE alembic_version')
        DbInfo.get_db().engine.execute('DROP VIEW sales_order_detail')
        DbInfo.get_db().session.commit()
        DbInfo.get_db().drop_all()
