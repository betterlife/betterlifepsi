import os


ROOT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


def apath(*relative_dirs):
    """ Takes a relative path (the the repository's root) and return
    its absolute path.

    :returns: absolute filesystem path
    """
    return os.path.join(ROOT_DIR, *relative_dirs)


APP_DIR = apath('psi')
MIGRATION_DIR = apath('psi', 'migrations')
