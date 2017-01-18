# encoding: utf-8
from psi.app.service import Info
from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from psi.app.models.data_security_mixin import DataSecurityMixin

db = Info.get_db()


class Preference(db.Model, DataSecurityMixin):
    __tablename__ = 'preference'
    id = Column(Integer, primary_key=True)
    def_so_incoming_type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_so_incoming_type = relationship('EnumValues', foreign_keys=[def_so_incoming_type_id])
    def_so_incoming_status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_so_incoming_status = relationship('EnumValues', foreign_keys=[def_so_incoming_status_id])

    def_so_exp_type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_so_exp_type = relationship('EnumValues', foreign_keys=[def_so_exp_type_id])
    def_so_exp_status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_so_exp_status = relationship('EnumValues', foreign_keys=[def_so_exp_status_id])

    def_po_logistic_exp_status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_po_logistic_exp_status = relationship('EnumValues', foreign_keys=[def_po_logistic_exp_status_id])
    def_po_logistic_exp_type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_po_logistic_exp_type = relationship('EnumValues', foreign_keys=[def_po_logistic_exp_type_id])

    def_po_goods_exp_status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_po_goods_exp_status = relationship('EnumValues', foreign_keys=[def_po_goods_exp_status_id])
    def_po_goods_exp_type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    def_po_goods_exp_type = relationship('EnumValues', foreign_keys=[def_po_goods_exp_type_id])

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    remark = Column(Text)

    @staticmethod
    def get():
        return db.session.query(Preference).get(1)
