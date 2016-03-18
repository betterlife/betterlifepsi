# coding=utf-8
from flask.ext.security import LoginForm as BaseLoginForm


class LoginForm(BaseLoginForm):
    from app import database
    from app.models import *
    from flask.ext.babelex import lazy_gettext
    from wtforms import fields
    email = fields.StringField(label=lazy_gettext('Email Address'),)
    password = fields.PasswordField(label=lazy_gettext('Password'))
    remember = fields.BooleanField(label=lazy_gettext('Remember Me'))