# coding=utf-8

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

# This import should behind above two lines
# To avoid Chinese character display issue
from psi.app import create_app, init_all

application = create_app()
init_all(application)

if __name__ == '__main__':
    application.run(debug=True, threaded=True)
