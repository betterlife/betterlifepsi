# coding=utf-8
import os
from flask import Flask, redirect
from flask_security import SQLAlchemyUserDatastore, Security
from flask.ext.debugtoolbar import DebugToolbarExtension
from raven.contrib.flask import Sentry


def run_app(custom_config=None):
    flask_app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

    if custom_config is None:
        import app.config as default_config
        flask_app.config.from_object(default_config)
    else:
        flask_app.config.from_object(custom_config)

    from flask_babelex import Babel

    babel = Babel(default_locale='zh_Hans_CN')
    babel.init_app(flask_app)

    toolbar = DebugToolbarExtension(flask_app)

    import logging
    from logging import StreamHandler

    log_handler = StreamHandler()
    flask_app.logger.setLevel(logging.DEBUG)  # set the desired logging level here
    flask_app.logger.addHandler(log_handler)

    from app.app_provider import AppInfo
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(flask_app)
    AppInfo.set_db(db)
    from app.models import User, Role
    db.init_app(flask_app)

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(flask_app, user_datastore)

    from app.views import init_admin_views
    init_admin_views(flask_app, db)

    # Init Sentry if not in debug mode
    if flask_app.config['DEBUG'] is not True:
        sentry = Sentry(flask_app)
    else:
        import logging

        # Disable werkzeug log
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    @flask_app.route('/')
    def hello():
        return redirect("/admin", code=302)

    @flask_app.before_request
    def before_request():
        pass

    @flask_app.teardown_request
    def teardown_request(exception):
        pass

    @flask_app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @babel.localeselector
    def get_locale():
        # Put your logic here. Application can store locale in
        # user profile, cookie, session, etc.
        return 'zh_CN'

    return flask_app


if not os.environ.get('TESTING'):
    app = run_app()
