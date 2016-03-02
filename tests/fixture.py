def get_test_client():
    import os
    import app.config as config
    config.TESTING = True
    config.SQLALCHEMY_DATABASE_URI = (os.environ.get('TEST_DATABASE_URL') or 'postgres://flask_sit:flask_sit@localhost:5432/flask_sit')
    config.WTF_CSRF_ENABLED = False
    import start
    start.application = start.create_app(config)
    start.db = start.init_all_return_db(start.application)
    return start.application.test_client()
