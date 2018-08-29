# encoding: utf-8
from psi.app.service import Info
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import backref, relationship

from psi.app.models.data_security_mixin import DataSecurityMixin

db = Info.get_db()


class ProductCategory(db.Model, DataSecurityMixin):
    __tablename__ = 'product_category'
    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(128), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('product_category.id'))
    parent_category = relationship('ProductCategory', remote_side=id,
                                   backref=backref('sub_categories', lazy='joined'))

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    def __unicode__(self):
        return self.code + " - " + self.name

    def __repr__(self):
        return self.code + " - " + self.name
