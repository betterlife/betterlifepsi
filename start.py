# coding=utf-8

import os
from flask import Flask

application = None


def create_app(custom_config=None):
    flask_app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

    if custom_config is None:
        import app.config as default_config
        flask_app.config.from_object(default_config)
    else:
        flask_app.config.from_object(custom_config)

    return flask_app


def init_flask_security(flask_app, database):
    from flask_security import SQLAlchemyUserDatastore, Security
    from app.models import User, Role
    user_datastore = SQLAlchemyUserDatastore(database, User, Role)
    Security(flask_app, user_datastore)


def init_admin_views(flask_app, database):
    from app.views import init_admin_views
    init_admin_views(flask_app, database)


def init_db(flask_app):
    from app.app_provider import AppInfo
    from flask_sqlalchemy import SQLAlchemy
    database = SQLAlchemy(flask_app)
    database.init_app(flask_app)
    AppInfo.set_db(database)
    return database

def init_babel(flask_app):
    from flask_babelex import Babel
    return Babel(default_locale='zh_Hans_CN', app=flask_app)


def init_logging(flask_app):
    from raven.contrib.flask import Sentry
    # Init Sentry if not in debug mode
    if flask_app.config['DEBUG'] is not True:
        Sentry().init_app(flask_app)
    else:
        # Set log level to debug and redirect all the logs to stand out
        import logging
        from logging import StreamHandler
        log_handler = StreamHandler()
        flask_app.logger.setLevel(logging.DEBUG)
        flask_app.logger.addHandler(log_handler)

        # Disable werkzeug log
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)


def init_debug_toolbar(flask_app):
    from flask.ext.debugtoolbar import DebugToolbarExtension
    if flask_app.config['DEBUG']:
        DebugToolbarExtension(flask_app)


def define_route_context(flask_app, db, babel):
    from werkzeug.utils import redirect

    @flask_app.route('/')
    def hello():
        return redirect("/admin", code=302)

    @flask_app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @babel.localeselector
    def get_locale():
        # Put your logic here. Application can store locale in
        # user profile, cookie, session, etc.
        return 'zh_CN'


def init_all(app):
    database = init_db(app)
    init_flask_security(app, database)
    init_admin_views(app, database)
    babel = init_babel(app)
    init_logging(app)
    define_route_context(app, database, babel)


if not os.environ.get('TESTING'):
    application = create_app()
    init_all(application)
