# coding=utf-8
import os
from flask import Flask, redirect
from flask_security import SQLAlchemyUserDatastore, Security
from flask.ext.debugtoolbar import DebugToolbarExtension
from raven.contrib.flask import Sentry

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

import app.config as config

app.config.from_object(config)

from flask_babelex import Babel

babel = Babel(default_locale='zh_Hans_CN')
babel.init_app(app)

toolbar = DebugToolbarExtension(app)

import os.path as op

import logging
from logging import StreamHandler

log_handler = StreamHandler()
app.logger.setLevel(logging.DEBUG)  # set the desired logging level here
app.logger.addHandler(log_handler)

db = None


def init_db_security_admin():
    from app.app_provider import AppInfo
    if AppInfo.get_db() is None:
        from flask_sqlalchemy import SQLAlchemy
        v_db = SQLAlchemy(app)
        AppInfo.set_db(v_db)
        from app.models import User, Role
        v_db.init_app(app)

        # Setup Flask-Security
        user_datastore = SQLAlchemyUserDatastore(v_db, User, Role)
        Security(app, user_datastore)

        from app.views import init_admin_views
        init_admin_views(app, v_db)
        return v_db
    return db


if not app.config['TESTING']:
    db = init_db_security_admin()

# Init Sentry if not in debug mode
if app.config['DEBUG'] is not True:
    sentry = Sentry(app)
else:
    import logging

    # Disable werkzeug log
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)


@app.route('/')
def hello():
    return redirect("/admin", code=302)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'] or True, use_reloader=False)


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
