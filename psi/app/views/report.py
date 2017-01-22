from flask import request
from flask_admin import BaseView
from flask_admin import expose
from flask_login import login_required

from app.utils import has_role


class ReportView(BaseView):
    @expose(url='/', methods=['GET', 'POST'])
    @login_required
    @has_role('report_view')
    def index(self):
        if request.method == 'GET':
            return self.render('report/report.html')
        elif request.method == 'POST':
            content = request.form['content']