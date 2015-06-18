# coding=utf-8
from database import init_database
from flask import Flask, request, session
from flask.ext.babelex import Babel

# configuration
from views import *
from menus import init_admin_views

DEBUG = True
SECRET_KEY = 'development key'
BABEL_DEFAULT_LOCALE = 'zh_CN'
BABEL_DEFAULT_TIMEZONE = 'CST'

app = Flask(__name__)
app.config.from_object(__name__)
db_session = init_database()
# babel = init_i18n(app)
babel = Babel(app, default_locale="zh_CN", default_timezone="CST")
admin = init_admin_views(app)

@babel.localeselector
def get_locale():
    override = request.args.get('lang')
    if override:
        session['lang'] = override
    lang = session.get('lang', 'zh_CN')
    print lang
    return lang

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
    db_session.remove()