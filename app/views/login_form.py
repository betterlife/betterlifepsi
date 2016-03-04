# coding=utf-8
from app import database
from app.models import *
from flask.ext.babelex import lazy_gettext
from flask.ext.security import LoginForm as BaseLoginForm
from wtforms import fields


class LoginForm(BaseLoginForm):
    email = fields.StringField(label=lazy_gettext('Email Address'),)
    password = fields.PasswordField(label=lazy_gettext('Password'))
    remember = fields.BooleanField(label=lazy_gettext('Remember Me'))