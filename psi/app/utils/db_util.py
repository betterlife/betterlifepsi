from psi.app.service import Info
from flask_login import current_user
from sqlalchemy import desc


def get_next_code(object_type, user=current_user):
    """
    Get next code of object
    :param object_type: Type of the model
    :param user User context, default to current login user.
    :return: Value of next available code field(current max code plus 1 and format to 6 decimal(with leading zeros)
    """
    db = Info.get_db()
    if hasattr(object_type, 'organization_id'):
        obj = db.session.query(object_type).filter_by(organization_id=user.organization_id).order_by(desc(object_type.id)).first()
    else:
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
    db = Info.get_db()
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
    db = Info.get_db()
    if hasattr(object_type, 'organization_id'):
        return db.session.query(object_type).filter_by(name=val, organization_id=user.organization_id).first()
    return db.session.query(object_type).filter_by(name=val).first()


def save_objects_commit(*objects):
    """
    Save objects and commit to database
    :param objects: Objects to save
    """
    db = Info.get_db()
    save_objects(objects)
    db.session.commit()


def save_objects(objects):
    """
    Save objects without commit them to database
    :param objects: objects to save 
    """
    db = Info.get_db()
    for obj in objects:
        if obj is not None:
            db.session.add(obj)


def delete_by_id(obj_type, id_to_del, commit=True):
    """
    Delete model object by value
    :type obj_type: db.Model
    :type id_to_del: int
    """
    db = Info.get_db()
    obj = db.session.query(obj_type).get(id_to_del)
    db.session.delete(obj)
    if commit:
        db.session.commit()


def get_result_raw_sql(sql):
    """
    Get first returned value of a raw sql as a tuple
    :param sql: The sql to execute
    :return: a tuple contains first result
    """
    res = Info.get_db().engine.execute(sql)
    results = res.fetchall()
    result = None
    for r in results:
        result = r
        break
    return result


def filter_by_organization(object_type, user=current_user):
    """
    Filter object by user's organization
    :param object_type: Object type to filter
    :param user: User('s Organization) to use for the filter
    :return: List of object filter by the user's organisation
    """
    db = Info.get_db()
    return db.session.query(object_type).filter_by(organization_id=user.organization_id).all()


def id_query_to_obj(obj_type, query):
    """
    Query for objects from a list of id
    :param obj_type: object type
    :param query: query to get list of ids
    :return: list of objects
    """
    db = Info.get_db()
    raw_result = query.all()
    ids = []
    for r in raw_result:
        ids.append(getattr(r, 'id'))
    obj_result = db.session.query(obj_type).filter(obj_type.id.in_(ids)).all()
    return obj_result


def get_next_id(obj_type):
    """
    Get next id of a obj_type
    :param obj_type: Object type
    :return: current id plus one
    """
    from sqlalchemy import text
    db = Info.get_db()
    sql = text("select nextval('{0}_id_seq')".format(obj_type.__tablename__))
    result = db.engine.execute(sql)
    next_val = 1
    for row in result:
        next_val = row[0]
    return next_val
