class AppInfo(object):
    _db = None

    def __init__(self):
        pass

    @staticmethod
    def set_db(db):
        AppInfo._db = db

    @staticmethod
    def get_db():
        return AppInfo._db
