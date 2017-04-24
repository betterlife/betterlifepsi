from decimal import Decimal

from psi.app import const
from psi.app.models.data_security_mixin import DataSecurityMixin
from psi.app.service import Info
from psi.app.utils.format_util import format_decimal
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

db = Info.get_db()


class InventoryInOutLink(db.Model, DataSecurityMixin):
    __tablename__ = 'inventory_in_out_link'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)

    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product', foreign_keys=[product_id])

    in_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    in_date = Column(DateTime, nullable=False)
    receiving_line_id = Column(Integer, ForeignKey('receiving_line.id'), nullable=False)
    receiving_line = relationship('ReceivingLine',
                                  backref=backref('inventory_links', uselist=True),
                                  foreign_keys=[receiving_line_id])

    out_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    out_date = Column(DateTime, nullable=False)
    out_quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)

    shipping_line_id = Column(Integer, ForeignKey('shipping_line.id'), nullable=False)
    shipping_line = relationship('ShippingLine',
                                 backref=backref('inventory_links', uselist=True),
                                 foreign_keys=[shipping_line_id])

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    remark = Column(Text)
