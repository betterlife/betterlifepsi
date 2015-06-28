# coding=utf-8
from flask import Flask,redirect
from flask.ext.security import SQLAlchemyUserDatastore, Security, login_required

app = Flask(__name__)

import config

app.config.from_object(config)

from flask_babelex import Babel
babel = Babel(default_locale='zh_Hans_CN')
babel.init_app(app)

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app_provider import AppInfo
AppInfo.set_app(app)
AppInfo.set_db(db)
from models import *
db.init_app(app)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from views import init_admin_views
admin = init_admin_views(app, db)
AppInfo.set_admin(admin)

@app.route('/')
@login_required
def hello():
    return redirect("/admin", code=302)

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

@babel.localeselector
def get_locale():
    # Put your logic here. Application can store locale in
    # user profile, cookie, session, etc.
    return 'zh_CN'

