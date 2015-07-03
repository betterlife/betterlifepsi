# encoding: utf-8

from app_provider import AppInfo
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import backref, relationship

db = AppInfo.get_db()

class EnumValues(db.Model):
    __tablename__ = 'enum_values'
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('enum_values.id'))
    type = relationship('EnumValues', remote_side=id,
                        backref=backref('type_values', lazy='dynamic'))
    code = Column(String(32), unique=True, nullable=False)
    display = Column(String(64), nullable=False)

    @staticmethod
    def type_filter(type_code):
        return AppInfo.get_db().session.query(EnumValues).\
            join(EnumValues.type, aliased=True).\
            filter_by(code=type_code)

    def __repr__(self):
        return self.display.encode('utf-8')

    def __unicode__(self):
        return self.display.encode('utf-8')