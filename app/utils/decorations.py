# encoding=utf-8
from functools import wraps

from flask import abort
from flask.ext.login import current_user
from app.utils.security_util import get_user_roles


def has_role(expect_role):
    """
    Check whether a user has the specific roles
    :param func:
    :param expect_role:
    :return:
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                user_roles = get_user_roles(current_user)
                return f(*args, **kwargs) if expect_role in user_roles else abort(403)
            else:
                abort(403)

        return decorated_function

    return decorator
