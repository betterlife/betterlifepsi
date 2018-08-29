# encoding: utf-8

from psi.app.service import Info
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import backref, relationship

from psi.app.models.data_security_mixin import DataSecurityMixin

db = Info.get_db()


class EnumValues(db.Model, DataSecurityMixin):
    __tablename__ = 'enum_values'
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('enum_values.id'))
    type = relationship('EnumValues', remote_side=id,
                        backref=backref('type_values', lazy='joined'))
    code = Column(String(32), unique=True, nullable=False)
    display = Column(String(64), nullable=False)

    @staticmethod
    def get(v_code):
        #def inner_find(code):
        return db.session.query(EnumValues).filter_by(code=v_code).first()
        #val = Info.get(v_code, inner_find)
        #return val

    @staticmethod
    def type_filter(type_code):
        return db.session.query(EnumValues). \
            join(EnumValues.type, aliased=True). \
            filter_by(code=type_code)

    def __repr__(self):
        return self.display

    def __unicode__(self):
        return self.display
