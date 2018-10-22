# coding=utf-8
import sys
import os


try:
    # This import should behind above two lines
    # To avoid Chinese character display issue
    from psi.app import create_app, init_all
except ImportError:
    # If os.getcwd() is _inside_ the psi package, add parent directory
    # to front of PATH so the interpreter can import the `psi` package
    _root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
    sys.path.insert(0, _root_dir)
    # Try the import again!
    from psi.app import create_app, init_all


application = create_app()
socket_io = init_all(application, migrate=False)
