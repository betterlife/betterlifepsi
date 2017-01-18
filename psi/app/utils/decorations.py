# encoding=utf-8
from functools import wraps

from flask_login import current_user

from psi.app.utils.security_util import default_action_on_error


def has_role(expect_role, action_on_error=default_action_on_error):
    """
    Check whether a user has the specific roles
    :param func:
    :param expect_role:
    :param action_on_error
    :return:
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                from psi.app.utils import user_has_role
                return f(*args, **kwargs) if user_has_role(expect_role) else action_on_error()
            else:
                return action_on_error()

        return decorated_function

    return decorator
