# coding=utf-8
import os
from app.init import create_app, init_all

application = create_app()
init_all(application)
