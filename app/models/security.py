# encoding: utf-8
from app import const
from app.database import DbInfo
from app.utils.db_util import id_query_to_obj
from flask_security import RoleMixin, UserMixin
from sqlalchemy import ForeignKey, Integer, select, desc, func, between
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy.sql.elements import and_

db = DbInfo.get_db()

roles_users = db.Table('roles_users',
                       db.Column('id', db.Integer(), primary_key=True),
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Organization(db.Model):
    """
    Organization, used to do data isolation
    """
    __tablename__ = 'organization'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    lft = db.Column(Integer, unique=True, nullable=False)
    right = db.Column(Integer, unique=True, nullable=False)

    @hybrid_property
    def parent(self):
        return (db.session.query(Organization).
                filter(and_(Organization.lft < self.lft, Organization.right > self.right))
                .order_by(desc(Organization.lft)).first())

    @parent.setter
    def parent(self, value):
        pass

    @parent.expression
    def parent(self):
        return (select([Organization])
                .where(Organization.lft < self.lft)
                .where(Organization.right > self.right).label('parent'))

    @hybrid_property
    def all_children(self):
        """
        Get immediate children of the organization
        Reference:
        http://mikehillyer.com/articles/managing-hierarchical-data-in-mysql/
        http://www.sitepoint.com/hierarchical-data-database/
        Generated SQL Sample:
        SELECT node.name, (COUNT(parent.name) - (sub_tree.depth + 1)) AS depth
        FROM nested_category AS node,
             nested_category AS parent,
             nested_category AS sub_parent,
             (
              SELECT node.name, (COUNT(parent.name) - 1) AS depth
              FROM nested_category AS node,
              nested_category AS parent
              WHERE node.lft BETWEEN parent.lft AND parent.rgt
              AND node.name = 'PORTABLE ELECTRONICS'
              GROUP BY node.name
              ORDER BY node.lft
             )AS sub_tree
             WHERE node.lft BETWEEN parent.lft AND parent.rgt
             AND node.lft BETWEEN sub_parent.lft AND sub_parent.rgt
             AND sub_parent.name = sub_tree.name
             GROUP BY node.name
             ORDER BY node.lft;
        """
        s_node = aliased(Organization, name='s_node')
        s_parent = aliased(Organization, name='s_parent')
        sub_tree = db.session.query(s_node.id, (func.count(s_parent.name) - 1).label('depth')). \
            filter(and_(between(s_node.lft, s_parent.lft, s_parent.right), s_node.id == self.id)) \
            .group_by(s_node.id, s_node.lft).order_by(s_node.lft).subquery()

        t_node = aliased(Organization, name='t_node')
        t_parent = aliased(Organization, name='t_parent')
        t_sub_parent = aliased(Organization, name='t_sub_parent')
        # Postgres does not support label as (func.count(t_parent.name) - (sub_tree.c.depth + 1)).label('xxx')
        # And have the field in having clause will cause issue.
        query = (db.session.query(t_node.id, t_node.name, (func.count(t_parent.name) - (sub_tree.c.depth + 1))).
                 filter(and_(between(t_node.lft, t_parent.lft, t_parent.right),
                             between(t_node.lft, t_sub_parent.lft, t_sub_parent.right),
                             t_node.id != self.id,  # Exclude current node --> itself
                             t_sub_parent.id == sub_tree.c.id))
                 .group_by(t_node.id, t_node.name, t_node.lft, 'depth')
                 .order_by(t_node.lft))
        obj_result = id_query_to_obj(Organization, query)
        return obj_result

    @all_children.setter
    def all_children(self, val):
        pass

    @all_children.expression
    def all_children(self):
        pass

    @hybrid_property
    def immediate_children(self):
        """
        Get immediate children of the organization
        Reference:
        http://mikehillyer.com/articles/managing-hierarchical-data-in-mysql/
        http://www.sitepoint.com/hierarchical-data-database/
        Generated SQL Sample:
        SELECT node.name, (COUNT(parent.name) - (sub_tree.depth + 1)) AS depth
        FROM nested_category AS node,
             nested_category AS parent,
             nested_category AS sub_parent,
             (
              SELECT node.name, (COUNT(parent.name) - 1) AS depth
              FROM nested_category AS node,
              nested_category AS parent
              WHERE node.lft BETWEEN parent.lft AND parent.rgt
              AND node.name = 'PORTABLE ELECTRONICS'
              GROUP BY node.name
              ORDER BY node.lft
             )AS sub_tree
             WHERE node.lft BETWEEN parent.lft AND parent.rgt
             AND node.lft BETWEEN sub_parent.lft AND sub_parent.rgt
             AND sub_parent.name = sub_tree.name
             GROUP BY node.name
             HAVING depth <= 1
             ORDER BY node.lft;
        """
        s_node = aliased(Organization, name='s_node')
        s_parent = aliased(Organization, name='s_parent')
        sub_tree = db.session.query(s_node.id, (func.count(s_parent.name) - 1).label('depth')). \
            filter(and_(between(s_node.lft, s_parent.lft, s_parent.right), s_node.id == self.id)) \
            .group_by(s_node.id, s_node.lft).order_by(s_node.lft).subquery()

        t_node = aliased(Organization, name='t_node')
        t_parent = aliased(Organization, name='t_parent')
        t_sub_parent = aliased(Organization, name='t_sub_parent')
        # Postgres does not support label as (func.count(t_parent.name) - (sub_tree.c.depth + 1)).label('xxx')
        # And have the field in having clause will cause issue.
        query = (db.session.query(t_node.id, t_node.name, (func.count(t_parent.name) - (sub_tree.c.depth + 1))).
                 filter(and_(between(t_node.lft, t_parent.lft, t_parent.right),
                             between(t_node.lft, t_sub_parent.lft, t_sub_parent.right),
                             t_node.id != self.id,  # Exclude current node --> itself
                             t_sub_parent.id == sub_tree.c.id))
                 .group_by(t_node.id, t_node.name, t_node.lft, 'depth')
                 .having((func.count(t_parent.name) - (sub_tree.c.depth + 1)) <= 1)
                 .order_by(t_node.lft))
        return id_query_to_obj(Organization, query)

    @immediate_children.setter
    def immediate_children(self, val):
        pass

    @immediate_children.expression
    def immediate_children(self):
        pass

    def __unicode__(self):
        return self.name


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    parent_id = db.Column(Integer, ForeignKey('role.id'))
    parent = relationship('Role', remote_side=id, backref=backref('sub_roles', lazy='joined'))

    def __unicode__(self):
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    display = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    locale_id = db.Column(Integer, ForeignKey('enum_values.id'))
    locale = relationship('EnumValues', foreign_keys=[locale_id])
    timezone_id = db.Column(Integer, ForeignKey('enum_values.id'))
    timezone = relationship('EnumValues', foreign_keys=[timezone_id])
    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='joined'))

    def __unicode__(self):
        return self.display

    @staticmethod
    def locale_filter():
        from app.models import EnumValues
        return EnumValues.type_filter(const.LANGUAGE_VALUES_KEY)

    @staticmethod
    def timezone_filter():
        from app.models import EnumValues
        return EnumValues.type_filter(const.TIMEZONE_VALUES_KEY)
