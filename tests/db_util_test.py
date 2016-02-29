import unittest


class TestCases(unittest.TestCase):
    def setUp(self):
        import os
        import app.config as config
        config.TESTING = True
        config.SQLALCHEMY_DATABASE_URI = (os.environ.get('TEST_DATABASE_URL') or 'postgres://flask_sit:flask_sit@localhost:5432/flask_sit')
        config.WTF_CSRF_ENABLED = False
        import start
        application = start.start(config)
        self.test_client = application.test_client()

    def test_get_next_code(self):
        from app.models.supplier import Supplier
        from app.utils import db_util
        next_code = db_util.get_next_code(Supplier)
        self.assertEqual('000001', next_code)
