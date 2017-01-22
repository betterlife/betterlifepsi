# coding=utf-8
# __init__.py under each sub-directory is needed for nose to pick up the test

import sys

import os

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.insert(0, os.getcwd() + "/psi")
