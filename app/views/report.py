from flask import request
from flask_admin import BaseView
from flask_admin import expose
from flask_login import login_required


class ReportView(BaseView):
    @expose(url='/', methods=['GET', 'POST'])
    @login_required
    def index(self):
        if request.method == 'GET':
            return self.render('report.html')
        elif request.method == 'POST':
            content = request.form['content']
