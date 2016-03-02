from app.init import create_app, init_all


def init_test_client():
    import os
    import app.config as config
    config.TESTING = True
    config.SQLALCHEMY_DATABASE_URI = (os.environ.get('TEST_DATABASE_URL') or 'postgres://flask_sit:flask_sit@localhost:5432/flask_sit')
    config.WTF_CSRF_ENABLED = False
    application = create_app(config)
    init_all(application)
    return application.test_client()


def login_as_admin(test_client):
    return test_client.post('/login', data=dict(email='support@betterlife.io', password='password'), follow_redirects=True)
