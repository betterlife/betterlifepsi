# coding=utf-8
import app_provider
from flask import url_for, request
from flask.ext.admin.consts import ICON_TYPE_GLYPH
from flask.ext.babelex import lazy_gettext
import flask_admin as admin
from flask.ext.security import current_user, logout_user, login_user
from models import Product
from views.product_inventory import ProductInventoryView
from views.login_form import LoginForm
from werkzeug.utils import redirect
from flask_admin import helpers, expose

class AdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return redirect(url_for('product_inventory.index_view'))

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated():
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(AdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))
