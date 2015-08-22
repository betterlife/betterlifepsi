# coding=utf-8
import unittest

import app.config as config
import os


class TestCases(unittest.TestCase):
    def setUp(self):
        config.TESTING = True
        config.DATABASE_URL = os.environ.get('TEST_DATABASE_URL') or \
                              'postgres://flask_sit:flask_sit@localhost:5432/flask_sit'
        config.WTF_CSRF_ENABLED = False
        import start
        start.db = start.init_db_security_admin()
        self.test_client = start.app.test_client()

    def tearDown(self):
        pass
        # app_provider.AppInfo.get_db().get_engine(app.app).execute(
        #     'ALTER SCHEMA public OWNER TO flask_sit')
        # app_provider.AppInfo.get_db().get_engine(app.app).execute(
        #     "drop schema public cascade")
        # app_provider.AppInfo.get_db().get_engine(app.app).execute(
        #     "create schema public")

    def test_empty_db(self):
        rv = self.test_client.get('/login')
        assert 302, rv.status_code
        self.assertAlmostEquals('utf-8', rv.charset)
        self.assertIn('<input id="email" name="email" type="text" value="">',
                      rv.data)
        self.assertIn('<input id="password" name="password" '
                      'type="password" value="">', rv.data)
        self.assertIn('<input id="submit" name="submit" type="submit"', rv.data)

    def test_login_seed_user(self):
        rv = self.test_client.post('/login',
                                   data=dict(email='support@betterlife.io',
                                             password='password'),
                                   follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        self.assertIn('Log out', rv.data)
        self.assertIn('首页', rv.data)
        self.assertIn('运营诊断', rv.data)
        self.assertIn('周售量', rv.data)

    def test_login_user_not_exist(self):
        rv = self.test_client.post('/login',
                                   data=dict(email='support1@betterlife.io',
                                             password='password'),
                                   follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        self.assertIn('Specified user does not exist', rv.data)
        self.assertIn('<input id="email" name="email" type="text" value="support1@betterlife.io">',
                      rv.data)
        self.assertIn('<input id="password" name="password" '
                      'type="password" value="">', rv.data)
        self.assertIn('<input id="submit" name="submit" type="submit"', rv.data)

    def test_login_user_wrong_password(self):
        rv = self.test_client.post('/login',
                                   data=dict(email='support@betterlife.io',
                                             password='password1'),
                                   follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        self.assertIn('Invalid password', rv.data)
        self.assertIn('<input id="email" name="email" type="text" value="support@betterlife.io">',
                      rv.data)
        self.assertIn('<input id="password" name="password" '
                      'type="password" value="">', rv.data)
        self.assertIn('<input id="submit" name="submit" type="submit"', rv.data)


if __name__ == '__main__':
    unittest.main()
