from app import AppInfo
from sqlalchemy import desc

db = AppInfo.get_db()


def get_next_code(object_type):
    """
    Get next code of object
    :param object_type: Type of the model
    :return: Value of next available code field(current max code plus 1 and format to 6 decimal(with leading zeros)
    """
    obj = db.session.query(object_type).order_by(desc(object_type.id)).first()
    return '{0:06d}'.format(1 + int(obj.code))


def get_by_external_id(object_type, external_id):
    """
    Get model object via external_id, a field names "external_id" should exists and type should be int
    :param object_type: Object type
    :param external_id: external id
    :return: The object if found, otherwise None
    """
    return db.session.query(object_type).filter_by(external_id=external_id).first()


def save_objects_commit(*objects):
    """
    Save object and commit to database
    :param objects: Objects to save
    """
    for obj in objects:
        AppInfo.get_db().session.add(obj)
    AppInfo.get_db().session.commit()


def delete_by_id(obj_type, id_to_del):
    """
    Delete model object by value
    :type obj_type: db.Model
    :type id_to_del: int
    """
    obj = obj_type.query.get(id_to_del)
    AppInfo.get_db().session.delete(obj)
    AppInfo.get_db().session.commit()
