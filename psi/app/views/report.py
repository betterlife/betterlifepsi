from flask import request
from flask_admin import BaseView
from flask_admin import expose
from flask_login import login_required

from psi.app.utils import has_role


class ReportView(BaseView):

    @expose(url='/', methods=['GET', 'POST'])
    @login_required
    @has_role('report_view')
    def index(self):
        if request.method == 'GET':
            report_html_template_file = request.base_url.split("/")[-2]
            return self.render('report/{0}.html'.format(report_html_template_file))
        elif request.method == 'POST':
            content = request.form['content']