from flask.ext.babelex import Babel


def init_i18n(app):
    babel = Babel(app, default_locale="zh_CN", default_timezone="CST")
    return babel
