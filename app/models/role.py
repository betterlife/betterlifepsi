# encoding=utf-8

from app.service import Info
from app.models.data_security_mixin import DataSecurityMixin
from flask_security import RoleMixin
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship, backref

db = Info.get_db()

roles_users = db.Table('roles_users',
                       db.Column('id', db.Integer(), primary_key=True),
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin, DataSecurityMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    parent_id = db.Column(Integer, ForeignKey('role.id'))
    parent = relationship('Role', remote_side=id, backref=backref('sub_roles', lazy='joined'))

    def __unicode__(self):
        return self.name

    def can_delete(self):
        return len(self.sub_roles) == 0
