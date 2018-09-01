# coding=utf-8
import os
import warnings
from psi.app.thirdparty.local_image_store import LocalImageStore
from flask_babelex import lazy_gettext

from psi.app.thirdparty.cloudinary_image_store import CloudinaryImageStore


class BaseConfig(object):
    BABEL_DEFAULT_LOCALE = 'en_US'
    BABEL_DEFAULT_TIMEZONE = 'CST'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
    SECURITY_REGISTERABLE = False
    SECURITY_CONFIRMABLE = False
    SECURITY_RECOVERABLE = False
    SECURITY_CHANGEABLE = False
    DEBUG = (os.environ.get('DEBUG') == "True")
    TESTING = (os.environ.get('TESTING') == "True")
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    WTF_CSRF_ENABLED = True
    IMAGE_STORE_SERVICE = CloudinaryImageStore
    # TODO: Move those business related settings to a table and make it changeable via UI.
    DEFAULT_DELIVER_DAY = 5
    DEFAULT_LEAD_DAY = 3
    DEFAULT_CATEGORY_ID = 1
    DASHBOARD_BI_URL = ""
    UPLOAD_TMP_FOLDER = '/tmp'
    BUILDER_URL_PREFIX = 'https://bitbucket.org/xqliu/psi/commits'
    GIT_URL_PREFIX = 'https://bitbucket.org/xqliu/psi/commits'
    IMAGE_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    abs_path = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(abs_path, ".." ,"static", "uploaded")
    NEED_ADVICE_UPDATE_SECONDS = 2*60 # IN Seconds

    security_messages = {
        'PASSWORD_MISMATCH': (lazy_gettext('Password does not match'), 'error'),
        'DISABLED_ACCOUNT': (lazy_gettext('Account is disabled'), 'error'),
        'EMAIL_NOT_PROVIDED': (lazy_gettext('Email not provided'), 'error'),
        'INVALID_EMAIL_ADDRESS': (lazy_gettext('Invalid email address'), 'error'),
        'PASSWORD_NOT_PROVIDED': (lazy_gettext('Password not provided'), 'error'),
        'INVALID_PASSWORD': (lazy_gettext('Invalid password'), 'error'),
        'USER_DOES_NOT_EXIST': (lazy_gettext('Specified user does not exist'), 'error'),
    }


class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = False 
    IMAGE_STORE_SERVICE = LocalImageStore
    SEND_FILE_MAX_AGE_DEFAULT = 1


class TestConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    TESTING_MODE = 'LOCAL'
    IMAGE_STORE_SERVICE = LocalImageStore
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'postgres://flask_sit:flask_sit@localhost:5432/flask_sit'
    WTF_CSRF_ENABLED = False


class CITestConfig(TestConfig):
    IMAGE_STORE_SERVICE = CloudinaryImageStore
    TESTING_MODE = 'CI'
    warnings.filterwarnings("ignore")
    warnings.warn("deprecated", DeprecationWarning)


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
