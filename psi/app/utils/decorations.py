# encoding=utf-8
import itertools
import logging
import math
import random
import time
from functools import wraps

from flask_login import current_user

from psi.app.utils.security_util import default_action_on_error


log = logging.getLogger(__name__)


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


def retry(times, timeout_scaler=0.2, exceptions=None):
    """A retry decorator. Exponential timeout plus some jitter

    :param times: integer number of times to retry
    :param timeout_scaler: float number of seconds to wait between calls
    :param exceptions: tuple of exceptions to retry on. defaults to all
    """
    if exceptions is None:
        exceptions = (Exception,)
    else:
        exceptions = tuple(exceptions)

    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            for attempt in itertools.count(1):
                exponential_time = math.pow(2, attempt - 1)
                jitter = random.uniform(0.75, 1.5)

                timeout = max(timeout_scaler * exponential_time * jitter, 0)
                try:
                    if attempt > 1:
                        log.info("Calling function '%s' attempt '%s'",
                                 fn.__name__, attempt)
                    else:
                        log.debug("Calling function '%s' attempt '%s'",
                                  fn.__name__, attempt)
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt > times:
                        raise
                if timeout:
                    time.sleep(timeout)
        return decorated
    return wrapper
