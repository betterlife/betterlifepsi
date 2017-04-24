# encoding: utf-8
from psi.app.service import Info
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy import Text
from sqlalchemy.orm import backref, relationship

from psi.app.models.data_security_mixin import DataSecurityMixin

db = Info.get_db()


class RelatedValues(db.Model, DataSecurityMixin):
    __tablename__ = 'related_values'
    id = Column(Integer, primary_key=True)
    from_object_id = Column(Integer, nullable=False)
    from_object_type = Column(Text, nullable=False)

    to_object_id = Column(Integer, nullable=False)
    to_object_type = Column(Text, nullable=False)

    relation_type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=True)
    relation_type = relationship('EnumValues', backref=backref('objects_with_relation', lazy='joined'))
    remark = Column(Text, nullable=True)
