# coding=utf-8
from app import app_provider
from flask.ext.admin.babel import gettext
from flask.ext.babelex import lazy_gettext
from app.models import *
from werkzeug.security import check_password_hash
from wtforms import form, fields, validators


class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()],
                               label=lazy_gettext('Login Name'), )
    password = fields.PasswordField(validators=[validators.required()],
                                    label=lazy_gettext('Password'))

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError(gettext('Invalid user'))

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
            # to compare plain text passwords use
            # if user.password != self.password.data:
            raise validators.ValidationError(gettext('Invalid password'))

        if not user.active:
            raise validators.ValidationError(gettext('User is disabled'))

    def get_user(self):
        db = app_provider.AppInfo.get_db()
        return db.session.query(User).filter_by(login=self.login.data).first()
