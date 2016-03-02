# encoding: utf-8
from app.database import DbInfo
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import backref, relationship

db = DbInfo.get_db()


class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(128), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('product_category.id'))
    parent_category = relationship('ProductCategory', remote_side=id,
                                   backref=backref('sub_categories', lazy='joined'))

    def __unicode__(self):
        return self.code.encode('utf-8') + " - " + self.name.encode('utf-8')

    def __repr__(self):
        return self.code.encode('utf-8') + " - " + self.name.encode('utf-8')
