class DbInfo(object):
    _db = None

    def __init__(self):
        pass

    @staticmethod
    def set_db(db):
        # This if is here to make sure there's
        # only one db instance
        if DbInfo._db is None:
            DbInfo._db = db

    @staticmethod
    def get_db():
        return DbInfo._db
