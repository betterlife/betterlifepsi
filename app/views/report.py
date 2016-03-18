from flask import request
from flask.ext.admin import BaseView
from flask.ext.admin import expose
from flask.ext.login import login_required


class ReportView(BaseView):
    @expose(url='/', methods=['GET', 'POST'])
    @login_required
    def index(self):
        if request.method == 'GET':
            return self.render('report.html')
        elif request.method == 'POST':
            content = request.form['content']
