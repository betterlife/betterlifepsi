# encoding=utf-8
from utils import db_util


def filter_by_organization(field, object_type):
    """
    Set field query for a edit or create form
    :param field: field to set the query
    :param object_type: object type to filter
    :return: field with query and _object_list set by the values
    """
    values = db_util.filter_by_organization(object_type)
    field.query = values
    # See https://github.com/flask-admin/flask-admin/issues/1261 for detail issue.
    if len(values) == 0:
        field._object_list = []
