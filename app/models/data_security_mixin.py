# encoding=utf-8


class DataSecurityMixin(object):
    """
    To control security on data level
    To decide whether a user could delete/edit a specific row.
    """

    def __init__(self):
        pass

    def can_delete(self):
        """
        Whether a user could delete a specif row.
        :return: True if can, otherwise false.
        """
        return True
