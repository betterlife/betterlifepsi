# coding=utf-8
from flask import Flask

app = Flask(__name__)

import config
app.config.from_object(config)

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app_provider import AppInfo
AppInfo.set_app(app)
AppInfo.set_db(db)
from models import *
db.init_app(app)

from views import init_admin_views
admin = init_admin_views(app, db)
AppInfo.set_admin(admin)

if __name__ == '__main__':
    app.run()

@app.before_request
def before_request():
    pass


@app.teardown_request
def teardown_request(exception):
    pass


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()