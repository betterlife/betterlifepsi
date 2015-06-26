# coding=utf-8
from flask import Flask
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
# 'python migrate.py db migrate'
#   - generate migration script from current schema version.
# 'python migrate.py db upgrade'
#   - migrate DB.
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

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()