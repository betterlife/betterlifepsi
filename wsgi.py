# coding=utf-8
from app.init import create_app, init_all

application = create_app()
init_all(application)