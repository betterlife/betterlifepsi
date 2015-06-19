class AppInfo():

    _app = None
    _db = None
    _admin = None

    def __init__(self):
        pass

    @staticmethod
    def get_app():
        return AppInfo._app

    @staticmethod
    def set_app(app):
        AppInfo._app = app

    @staticmethod
    def set_db(db):
        AppInfo._db = db

    @staticmethod
    def get_db():
        return AppInfo._db

    @staticmethod
    def set_admin(admin):
        AppInfo._admin = admin

    @staticmethod
    def get_admin():
        return AppInfo._admin