# coding=utf-8

from flask import url_for, request
from flask.ext.admin import BaseView
import flask_admin as admin
from flask.ext.security import current_user, \
    url_for_security
from werkzeug.utils import redirect
from flask_admin import expose


class AdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated():
            return redirect(url_for_security('login'))
        return redirect(url_for('product_inventory.index_view'))


class ImportStoreDataView(BaseView):
    @expose(url='/', methods=['GET', 'POST'])
    def index(self):
        if not current_user.is_authenticated():
            return redirect(url_for_security('login'))
        if request.method == 'GET':
            return self.render('data_loading/legacy.html')
        elif request.method == 'POST':
            return self.render('data_loading/legacy.html')
