# coding=utf-8
from flask import Flask
from flask.ext.migrate import Migrate, MigrateCommand
from raven.contrib.flask import Sentry
from flask.ext.script import Manager
# 'python manage.py db migrate'
#   - generate migration script from current schema version.
# 'python manage.py db upgrade'
#   - migrate DB.
app = Flask(__name__)

import app.config as config

app.config.from_object(config)

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
from app.app_provider import AppInfo

AppInfo.set_app(app)
AppInfo.set_db(db)
db.init_app(app)

# Init Sentry if not in debug mode
if app.config['DEBUG'] is not True:
    app.config[
        'SENTRY_DSN'] = 'https://9f6d2c7e33f24b77baba8a3e17a6dcfa:0afc65c1b9124c61adae430fad653718@app.getsentry.com' \
                        '/50555'
    sentry = Sentry(app)

if __name__ == '__main__':
    migrate = Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.run()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()
