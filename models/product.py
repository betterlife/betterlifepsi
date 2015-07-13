# encoding: utf-8
from decimal import Decimal
from app_provider import AppInfo
from models.util import format_decimal
from models.inventory_transaction import InventoryTransactionLine
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Text, select, func
from sqlalchemy.ext.hybrid import hybrid_property
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

    @hybrid_property
    def in_transit_quantity(self):
        i_ts = self.inventory_transaction_lines
        total = 0
        if len(i_ts) > 0:
            for l in i_ts:
                if l.in_transit_quantity is not None:
                    total += l.in_transit_quantity
        return total

    @in_transit_quantity.setter
    def in_transit_quantity(self, val):
        pass

    @in_transit_quantity.expression
    def in_transit_quantity(self):
        return (select([func.sum(InventoryTransactionLine.in_transit_quantity)])
                .where(self.id == InventoryTransactionLine.product_id)
                .label('in_transit_stock'))

    @hybrid_property
    def available_quantity(self):
        i_ts = self.inventory_transaction_lines
        total = 0
        if len(i_ts) > 0:
            for l in i_ts:
                if l.quantity is not None:
                    total += l.quantity
        return total

    @available_quantity.setter
    def available_quantity(self, val):
        pass

    @available_quantity.expression
    def available_quantity(self):
        return (select([func.sum(InventoryTransactionLine.quantity)])
                .where(self.id == InventoryTransactionLine.product_id)
                .label('available_quantity'))

    @staticmethod
    def supplier_filter(s_id):
        return AppInfo.get_db().session.query(Product).filter_by(supplier_id=s_id)

    def __unicode__(self):
        return self.supplier.name + ' - ' + self.name + ' - P:' \
               + str(self.purchase_price) + ' - R:' + str(self.retail_price)

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return self.name
