# encoding=utf-8
from functools import wraps

from flask import abort
from flask_login import current_user


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
                from app.utils.security_util import user_has_role
                return f(*args, **kwargs) if user_has_role(expect_role) else abort(403)
            else:
                abort(403)

        return decorated_function

    return decorator
