# encoding: utf-8
from psi.app import const
from psi.app.models.inventory_transaction import InventoryTransactionLine, \
    InventoryTransaction
from psi.app.service import Info
from psi.app.utils.date_util import get_weeks_between
from psi.app.utils.format_util import format_decimal
from flask_login import current_user
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Text, \
    select, func, Boolean, or_, event, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

from psi.app.models.data_security_mixin import DataSecurityMixin

db = Info.get_db()


class ProductImage(db.Model, DataSecurityMixin):
    __tablename__ = 'product_image'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    # The product image need to be delete when a product got deleted
    product = relationship('Product', backref=backref('images', cascade='all, delete'))
    image_id = Column(Integer, ForeignKey('image.id'), nullable=False)
    # The image need to be delete when a product image got deleted
    image = relationship('Image', cascade="all, delete")


class Product(db.Model, DataSecurityMixin):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=False, nullable=False)
    external_id = Column(String(), nullable=True, unique=False)
    deliver_day = Column(Integer, nullable=False)
    lead_day = Column(Integer, nullable=False)
    distinguishing_feature = Column(Text)
    spec_link = Column(String(128))
    purchase_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    retail_price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    franchise_price = Column(Numeric(precision=8, scale=2,
                                     decimal_return_scale=2), nullable=True)
    category_id = Column(Integer, ForeignKey('product_category.id'), nullable=False)
    category = relationship('ProductCategory', backref=backref('products', lazy='joined'))
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier = relationship('Supplier', backref=backref('products', lazy='dynamic'))
    need_advice = Column(Boolean)
    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    mnemonic = Column(String(128), unique=False, nullable=True)

    create_date = Column(DateTime, nullable=False)
    # 1. We need to add a create_date to product to support the daily average profit
    #   1. Add the field to product model
    #   2. Add the database migration script
    #   3. Calculate create date of existing product and fill to DB.
    # 2. Calculate the total profit
    # 3. Calculate how many days this supplier exists in the system.
    # 4. Calculate average daily profit using the formula total profit/days supplier exists.
    # 5. Need to take care if the days calculated is 0 --> Avoid Zero Divide Exception
    # Question:
    #   1. What will the logic looks like if the create date is null?
    #     -> If the create date is null, use oldest date of current product's purchase order
    #   2. What value should create_date of existing product be set to?
    #     -> Set the create date to oldest date of current product's purchase order works?
    #   3. How to calculate number of days between product's create date and now?
    #     -> select date_part('day', now() - order_date) as age from purchase_order;

    @hybrid_property
    def images_placeholder(self):
        return self.images

    @images_placeholder.setter
    def images_placeholder(self, val):
        pass

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
                .label('in_transit_quantity'))

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
        return Info.get_db().session.query(Product).filter_by(supplier_id=s_id)

    @staticmethod
    def organization_filter(o_id):
        return Info.get_db().session.query(Product).filter_by(organization_id=o_id)

    def get_lead_deliver_day(self):
        if self.deliver_day is None and self.lead_day is None:
            return 0
        elif self.deliver_day is None:
            return self.lead_day
        elif self.lead_day is None:
            return self.deliver_day
        return self.deliver_day + self.lead_day

    def get_profit_lost_caused_by_inventory_short(self):
        if self.average_unit_profit == 0 or self.weekly_sold_qty == 0:
            return 0
        can_sell_day = format_decimal(self.available_quantity / self.weekly_sold_qty) * 7
        days_without_prd = (self.get_lead_deliver_day() - can_sell_day)
        return self.average_unit_profit * self.weekly_sold_qty * days_without_prd / 7

    def __unicode__(self):
        from psi.app.utils import user_has_role
        result = self.name
        if user_has_role('supplier_view'):
            result += "/供应商:{0}".format(self.supplier.name[:6])
        if (user_has_role('purchase_price_view') and
            current_user.organization.type.code ==
            const.DIRECT_SELLING_STORE_ORG_TYPE_KEY):
            result += "/进货价:{0}".format(self.purchase_price)
            result += '/零售价:{0}'.format(self.retail_price)
        elif (user_has_role('purchase_price_view') and
            current_user.organization.type.code ==
            const.FRANCHISE_STORE_ORG_TYPE_KEY):
            result += "/拿货价:{0}".format(self.franchise_price)
            result += '/建议零售价:{0}'.format(self.retail_price)
        return result

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return self.name
