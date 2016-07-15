class Info(object):
    _db = None

    def __init__(self):
        pass

    @staticmethod
    def set_db(db):
        # This if is here to make sure there's
        # only one db instance
        if Info._db is None:
            Info._db = db

    @staticmethod
    def get_db():
        return Info._db
