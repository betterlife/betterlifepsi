# coding=utf-8

import sys

import os

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.insert(0, os.getcwd() + "/psi")

# This import should behind above two lines
# To avoid Chinese character display issue
from psi.app import create_app, init_all

application = create_app()
socket_io = init_all(application)

if __name__ == '__main__':
    application.run(threaded=True, debug=True)
