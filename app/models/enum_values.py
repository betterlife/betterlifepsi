# encoding: utf-8

from app.database import DbInfo
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import backref, relationship

db = DbInfo.get_db()


class EnumValues(db.Model):
    __tablename__ = 'enum_values'
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('enum_values.id'))
    type = relationship('EnumValues', remote_side=id,
                        backref=backref('type_values', lazy='joined'))
    code = Column(String(32), unique=True, nullable=False)
    display = Column(String(64), nullable=False)

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    @staticmethod
    def find_one_by_code(v_code):
        v_l = db.session.query(EnumValues).filter_by(code=v_code).all()
        return v_l[0]

    @staticmethod
    def type_filter(type_code):
        return db.session.query(EnumValues).\
            join(EnumValues.type, aliased=True).\
            filter_by(code=type_code)

    def __repr__(self):
        return self.display.encode('utf-8')

    def __unicode__(self):
        return self.display.encode('utf-8')
