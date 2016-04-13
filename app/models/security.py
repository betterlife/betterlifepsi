# encoding: utf-8
from app import const
from app.database import DbInfo
from flask.ext.security import RoleMixin, UserMixin
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship, backref

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
    parent_id = db.Column(Integer, ForeignKey('organization.id'))
    parent = relationship('Organization', remote_side=id, backref=backref('sub_organizations', lazy='joined'))

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
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
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
