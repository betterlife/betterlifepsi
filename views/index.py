# coding=utf-8
import app_provider
from flask import url_for, request
import flask_admin as admin
from flask.ext.security import current_user, logout_user, login_user
from werkzeug.utils import redirect
from flask_admin import helpers, expose

class AdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(AdminIndexView, self).index()

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
