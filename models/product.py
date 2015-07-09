# encoding: utf-8
from app_provider import AppInfo
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Text
from sqlalchemy.orm import backref, relationship

db = AppInfo.get_db()

class Product(db.Model):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(128), unique=True, nullable=False)
    deliver_day = Column(Integer)
    lead_day = Column(Integer)
    distinguishing_feature = Column(Text)
    spec_link = Column(String(128))
    purchase_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    retail_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    category_id = Column(Integer, ForeignKey('product_category.id'), nullable=False)
    category = relationship('ProductCategory', backref=backref('products', lazy='dynamic'))
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier = relationship('Supplier', backref=backref('products', lazy='dynamic'))

    @staticmethod
    def supplier_filter(s_id):
        return AppInfo.get_db().session.query(Product).filter_by(supplier_id=s_id)

    def __unicode__(self):
        return self.supplier.name + ' - ' + self.name + ' - P:' \
               + str(self.purchase_price) + ' - R:' + str(self.retail_price)

    def __repr__(self):
        return self.__unicode__
