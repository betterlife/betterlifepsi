from app.database import DbInfo
from flask.ext.login import current_user
from sqlalchemy import desc


def get_next_code(object_type):
    """
    Get next code of object
    :param object_type: Type of the model
    :return: Value of next available code field(current max code plus 1 and format to 6 decimal(with leading zeros)
    """
    db = DbInfo.get_db()
    obj = db.session.query(object_type).order_by(desc(object_type.id)).first()
    if obj is None:
        return '{0:06d}'.format(1)
    return '{0:06d}'.format(1 + int(obj.code))


def get_by_external_id(object_type, external_id, user=current_user):
    """
    Get model object via external_id, a field names "external_id" should exists
    :param object_type: Object type
    :param external_id: external id
    :param user: user context, default to current login user.
    :return: The object if found, otherwise None
    """
    db = DbInfo.get_db()
    if hasattr(object_type, 'organization_id'):
        return db.session.query(object_type).filter_by(external_id=external_id, organization_id=user.organization_id).first()
    return db.session.query(object_type).filter_by(external_id=external_id).first()


def get_by_name(object_type, val, user=current_user):
    """
    Get the first model object via query condition of name field
    :param object_type: Object type
    :param val: value of the name
    :param user: user context, default to current login user.
    :return: The object if found, otherwise None
    """
    db = DbInfo.get_db()
    if hasattr(object_type, 'organization_id'):
        return db.session.query(object_type).filter_by(name=val, organization_id=user.organization_id).first()
    return db.session.query(object_type).filter_by(name=val).first()


def save_objects_commit(*objects):
    """
    Save object and commit to database
    :param objects: Objects to save
    """
    db = DbInfo.get_db()
    for obj in objects:
        db.session.add(obj)
    db.session.commit()


def delete_by_id(obj_type, id_to_del):
    """
    Delete model object by value
    :type obj_type: db.Model
    :type id_to_del: int
    """
    db = DbInfo.get_db()
    obj = db.session.query(obj_type).get(id_to_del)
    db.session.delete(obj)
    db.session.commit()
