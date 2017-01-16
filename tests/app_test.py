# coding=utf-8
import unittest

from tests import fixture
from tests.base_test_case import BaseTestCase


class TestApplicationStartupAndLogin(BaseTestCase):

    def test_empty_db(self):
        rv = self.test_client.get('/login')
        assert 302, rv.status_code
        self.assertAlmostEquals('utf-8', rv.charset)
        self.assertIn('<input id="email_or_login" name="email_or_login" type="text" value="">', rv.data)
        self.assertIn('<input id="password" name="password" type="password" value="">', rv.data)
        self.assertIn('<input id="submit" name="submit" type="submit"', rv.data)

    def test_login_seed_user(self):
        rv = self.test_client.post('/login', data=dict(email_or_login='support@betterlife.io', password='password'), follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        self.assertIn('Log out', rv.data)
        self.assertIn('Home', rv.data)

    def test_login_user_not_exist(self):
        rv = self.test_client.post('/login', data=dict(email_or_login='support1@betterlife.io', password='password'), follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        self.assertIn('Specified user does not exist', rv.data)
        self.assertIn('<input id="email_or_login" name="email_or_login" type="text" value="support1@betterlife.io">', rv.data)
        self.assertIn('<input id="password" name="password" type="password" value="">', rv.data)
        self.assertIn('<input id="submit" name="submit" type="submit"', rv.data)

    def test_login_user_wrong_password(self):
        rv = self.test_client.post('/login', data=dict(email_or_login='support@betterlife.io', password='password1'), follow_redirects=True)
        self.assertEqual(200, rv.status_code)
        self.assertIn('Invalid password', rv.data)
        self.assertIn('<input id="email_or_login" name="email_or_login" type="text" value="support@betterlife.io">', rv.data)
        self.assertIn('<input id="password" name="password" type="password" value="">', rv.data)
        self.assertIn('<input id="submit" name="submit" type="submit"', rv.data)


if __name__ == '__main__':
    unittest.main()
