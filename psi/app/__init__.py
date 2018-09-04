# encoding=utf-8

import os
import code
import traceback
import signal

from flask_babelex import gettext

from psi.app import const
from psi.app.service import Info

__version__ = '0.6.7-4'


def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message = "Signal received : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)


def listen():
    signal.signal(signal.SIGUSR1, debug)  # Register handler


listen()


def create_app(custom_config=None):
    from flask import Flask

    flask_app = Flask(__name__, template_folder='../templates', static_folder='../static')

    if custom_config is not None:
        active_config = custom_config
    else:
        import psi.app.config as default_config
        if os.environ.get('DEBUG') == 'True':
            active_config = default_config.DevConfig
        else:
            active_config = default_config.ProductionConfig
    active_config.VERSION = __version__
    flask_app.config.from_object(active_config)

    return flask_app


def init_flask_security(flask_app, database):
    from flask_security import SQLAlchemyUserDatastore, Security
    from psi.app.models.user import User
    from psi.app.models.role import Role
    import psi.app.config as config
    for key, value in config.BaseConfig.security_messages.items():
        flask_app.config['SECURITY_MSG_' + key] = value
    user_datastore = SQLAlchemyUserDatastore(database, User, Role)
    from psi.app.views.login_form import LoginForm
    security = Security(flask_app, user_datastore, login_form=LoginForm)
    return security


def init_admin_views(flask_app, database):
    from psi.app.views import init_admin_views
    return init_admin_views(flask_app, database)


def init_db(flask_app):
    from flask_sqlalchemy import SQLAlchemy
    sqlalchemy = SQLAlchemy(flask_app, session_options={'autoflush': False})
    sqlalchemy.init_app(flask_app)
    Info.set_db(sqlalchemy)
    return sqlalchemy


def init_migrate(flask_app, database):
    from flask_migrate import Migrate, upgrade

    Migrate(app=flask_app, db=database)
    with flask_app.app_context():
        upgrade(directory=os.path.dirname(__file__) + "/../migrations")


def init_babel(flask_app):
    from flask_babelex import Babel
    # return Babel(default_locale='zh_Hans_CN', app=flask_app)
    return Babel(app=flask_app)


def init_logging(flask_app):
    from raven.contrib.flask import Sentry
    import logging
    from logging import FileHandler
    from logging import Formatter
    logger = logging.getLogger('psi')
    if flask_app.config['DEBUG']:
        # set environment variable WERKZEUG_DEBUG_PIN to off to
        # disable debug PIN for werkzeug.
        # log = logging.getLogger('werkzeug')
        # log.setLevel(logging.INFO)
        # file_handler = FileHandler('betterlife-psi.log', encoding='UTF-8', mode='w')
        # file_handler.setFormatter(Formatter(const.FILE_HANDLER_LOG_FORMAT))
        # logger.addHandler(file_handler)
        #logger.setLevel(logging.DEBUG)
        pass
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(Formatter(const.CONSOLE_HANDLER_LOG_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        Sentry(flask_app, logging=True, level=logging.INFO)


def init_debug_toolbar(flask_app):
    from flask_debugtoolbar import DebugToolbarExtension
    if flask_app.config['DEBUG']:
        flask_app.debug = True
        DebugToolbarExtension(flask_app)


def define_route_context(flask_app, db, babel):
    from werkzeug.utils import redirect
    from flask_login import current_user
    from flask import request, current_app

    @flask_app.route('/')
    def hello():
        return redirect("/admin", code=302)

    @flask_app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @babel.timezoneselector
    def get_timezone():
        if getattr(current_user, 'timezone', None) is not None:
            return current_user.timezone.code
        return 'CST' if current_app.config['DEBUG'] else "UTC"

    @babel.localeselector
    def get_locale():
        """
        Put your logic here. Application can store locale in
        user profile, cookie, session, etc.
        This is the setting actually take effective
        """
        try:
            if getattr(current_user, 'locale', None) is not None:
                return current_user.locale.code
            return 'zh_CN' if current_app.config['DEBUG'] else \
                   request.accept_languages.best_match(['zh_CN', 'en_US'])
        except BaseException:
            return 'zh_CN' if current_app.config['DEBUG'] else \
                   request.accept_languages.best_match(['zh_CN', 'en_US'])


def init_https(app):
    # only trigger SSLify if the app is running on Heroku and debug is false
    if (app.config['DEBUG'] is False) and ('DYNO' in os.environ):
        from flask_sslify import SSLify
        SSLify(app)


def init_jinja2_functions(app):
    from psi.app.utils.ui_util import render_version, has_detail_field, \
        is_inline_field, is_list_field
    app.add_template_global(render_version, 'render_version')
    app.add_template_global(has_detail_field, 'has_detail_field')
    app.add_template_global(is_inline_field, 'is_inline_field')
    app.add_template_global(is_list_field, 'is_list_field')
    app.add_template_global(gettext, 'mytext')


def init_image_service(app):
    """
    Initialize image store service
    """
    image_store = app.config['IMAGE_STORE_SERVICE']
    if image_store is not None:
        Info.set_image_store_service(image_store(app))


def init_flask_restful(app):
    """
    Initialize flask restful api
    """
    from flask_restful import Api
    from psi.app.api import init_all_apis
    flask_restful = Api(app)
    init_all_apis(flask_restful)
    return flask_restful


def init_reports(app, api):
    """
    Init reports
    """
    from psi.app.reports import init_report_endpoint
    init_report_endpoint(app, api)


def init_socket_io(app):
    from flask_socketio import SocketIO
    from psi.app.socketio import init_socket_tio_handlers
    socket_io = SocketIO(app)
    init_socket_tio_handlers(socket_io)
    return socket_io


def init_all(app, migrate=True):
    init_logging(app)
    # === Important notice to the maintainer ===
    # This line was use to database = init_db(app)
    # But we found session can not be cleaned among different
    # Unit tests, so we add this to avoid issue
    # sqlalchemy-object-already-attached-to-session
    # http://stackoverflow.com/questions/24291933/sqlalchemy-object-already-attached-to-session
    # A similar issue was captured on
    # https://github.com/jarus/flask-testing/issues/32
    # Please don't try to modify the follow four lines.
    # Please don't try to modify the follow four lines.
    # Please don't try to modify the follow four lines.
    if Info.get_db() is None:
        database = init_db(app)
    else:
        database = Info.get_db()
        database.init_app(app)
    if migrate:
        init_migrate(app, database)
    init_https(app)
    security = init_flask_security(app, database)
    init_admin_views(app, database)
    babel = init_babel(app)
    api = init_flask_restful(app)
    init_reports(app, api)
    init_jinja2_functions(app)
    # init_debug_toolbar(app)
    init_image_service(app)
    socket_io = init_socket_io(app)
    define_route_context(app, database, babel)

    # define a context processor for merging flask-admin's template context
    # into the flask-security views.
    @security.context_processor
    def security_context_processor():
        from flask import url_for
        return dict(
            get_url=url_for
        )

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        database = Info.get_db()
        database.session.remove()

    return socket_io
