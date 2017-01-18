# coding=utf-8
from flask_security.utils import get_message
from flask_security import LoginForm as BaseLoginForm
from flask_security.forms import _datastore
from flask_security.utils import verify_and_update_password
from flask_babelex import lazy_gettext
from wtforms import fields


class LoginForm(BaseLoginForm):

    email_or_login = fields.StringField(label=lazy_gettext('Email Address or Login Name'),)
    password = fields.PasswordField(label=lazy_gettext('Password'))
    remember = fields.BooleanField(label=lazy_gettext('Remember Me'))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def validate(self):
        self.email_or_login.errors, self.password.errors = [], []
        if self.email_or_login.data.strip() == '':
            self.email_or_login.errors.append(get_message('LOGIN_NOT_PROVIDED')[0])
            return False

        if self.password.data.strip() == '':
            self.password.errors.append(get_message('PASSWORD_NOT_PROVIDED')[0])
            return False

        self.user = _datastore.find_user(login=self.email_or_login.data.strip())
        if self.user is None:
            self.user = _datastore.find_user(email=self.email_or_login.data.strip())

        if self.user is None:
            self.email_or_login.errors.append(get_message('USER_DOES_NOT_EXIST')[0])
            return False
        if not self.user.password:
            self.password.errors.append(get_message('PASSWORD_NOT_SET')[0])
            return False
        if not verify_and_update_password(self.password.data, self.user):
            self.password.errors.append(get_message('INVALID_PASSWORD')[0])
            return False
        if not self.user.is_active:
            self.email_or_login.errors.append(get_message('DISABLED_ACCOUNT')[0])
            return False
        return True