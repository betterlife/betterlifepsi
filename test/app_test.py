import unittest

import app


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        # self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()
        # app.init_database()

    def tearDown(self):
        pass
        # os.unlink(app.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 302, rv.status_code
        assert '/admin' in rv.location
        assert 'utf-8', rv.charset
        return

if __name__ == '__main__':
    unittest.main()
