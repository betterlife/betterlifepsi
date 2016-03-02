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
from app.database import DbInfo

DbInfo.set_db(db)
from app.models import *
db.init_app(app)

# Init Sentry if not in debug mode
if not app.config.get('DEBUG'):
    sentry = Sentry(app)

if __name__ == '__main__':
    migrate = Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.run()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()
