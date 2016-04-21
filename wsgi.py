# coding=utf-8

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

from app import create_app, init_all

application = create_app()
init_all(application)

if __name__ == '__main__':
    application.run()
