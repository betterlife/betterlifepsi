# encoding=utf-8
from functools import wraps

from flask import current_app
from flask.ext.login import current_user
from utils.security_util import get_user_roles


def has_any_role(expect_roles):
    """
    Check whether a user has the specific roles
    :param func:
    :param expect_roles:
    :return:
    """

    def decorated_view(func, *args, **kwargs):
        #TODO to see how to judge a local proxy is None?
        if current_user is not None and current_user.is_authenticated:
            user_roles = get_user_roles(current_user)
            for r in expect_roles:
                if r in user_roles:
                    return func(*args, **kwargs)
        else:
            return current_app.login_manager.unauthorized()

    return decorated_view
