# encoding: utf-8
from decimal import Decimal

from app import const
from app.models.data_security_mixin import DataSecurityMixin
from app.service import Info
from app.utils.format_util import format_decimal
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

db = Info.get_db()


class InventoryTransaction(db.Model, DataSecurityMixin):
    __tablename__ = 'inventory_transaction'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    type_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    type = relationship('EnumValues', foreign_keys=[type_id])

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    remark = Column(Text)

    @staticmethod
    def type_filter():
        from app.models.enum_values import EnumValues
        return EnumValues.type_filter(const.INVENTORY_TRANSACTION_TYPE_KEY)

    @staticmethod
    def manual_type_filter():
        from app.models.enum_values import EnumValues
        from sqlalchemy import or_
        q = db.session.query(EnumValues).filter(or_(EnumValues.code == const.INVENTORY_LOST_TYPE_KEY,
                                                    EnumValues.code == const.INVENTORY_DAMAGED_TYPE_KEY))
        return q




    @hybrid_property
    def total_amount(self):
        return format_decimal(Decimal(abs(sum(line.total_amount for line in self.lines))))

    @total_amount.expression
    def total_amount(self):
        return (select([func.sum(InventoryTransactionLine.price
                                 * (InventoryTransactionLine.in_transit_quantity
                                    + InventoryTransactionLine.quantity))])
                .where(self.id == InventoryTransactionLine.inventory_transaction_id)
                .label('total_amount'))

    @total_amount.setter
    def total_amount(self, value):
        pass

    def __unicode__(self):
        return str(self.id)


class InventoryTransactionLine(db.Model):
    __tablename = 'inventory_transaction_line'
    id = Column(Integer, primary_key=True)
    in_transit_quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=True)
    quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product', backref=backref('inventory_transaction_lines'))
    price = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    # 每次采购入库, 把in_transit_quantity设置为0，quantity设置为入库数量的时候，
    # 把这个saleable_quantity 设置为和quantity相同
    # 每次某产品A销售出库的时候，找出所有的这个A产品的，saleable_quantity不为0的入库行，按照时间排序，最早的排在最前面
    # 使用递归，从最前面循环，从入库行的 saleable_quantity 字段中，减去本次销售的数量
    # 如果一个入库行不够减的，则继续减第二个入库行的（注意所有查询出来的入库行按照时间排序，最早的排在最前面）
    # 同时创建一个新的Model，其字段如下
    # 产品，入库价格、入库时间，出库价格、出库时间，出库数量，关联出库单（销售发货单），关联入库单（采购收货单）
    # 在销售出库的时候，写这个表，如果一个产品的一次销售要用到两次的入库库存，则创建两个如上的记录
    # 通过这种方式记录每次销售的库存都是从哪个入库库存(采购单)来的，从而知道这次销售的库存的成本是多少
    # 计算某个时间段的利润的时候，使用新增加的表中的记录来计算
    # 按照在该段时间里面出库的产品，使用如下的公式：
    # (出库价格 - 入库价格) * 出库数量
    # 过滤条件为：对应的时间段
    # 这样算出来的利润就是按照先进先出方法算出来的最准确的利润了。
    saleable_quantity = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=True)
    remark = Column(Text)
    inventory_transaction_id = Column(Integer, ForeignKey('inventory_transaction.id'), nullable=False)
    inventory_transaction = relationship('InventoryTransaction',
                                         backref=backref('lines', cascade='all, delete-orphan'))

    @hybrid_property
    def type(self):
        return self.inventory_transaction.type

    @type.setter
    def type(self, value):
        pass

    @hybrid_property
    def date(self):
        return self.inventory_transaction.date

    @date.setter
    def date(self, value):
        pass

    @hybrid_property
    def total_amount(self):
        q = 0 if self.quantity is None else self.quantity
        i_t_q = 0 if self.in_transit_quantity is None else self.in_transit_quantity
        return format_decimal(Decimal(abs(self.price * (q + i_t_q))))

    @total_amount.expression
    def total_amount(self):
        return select([self.price * (self.quantity + self.in_transit_quantity)]).label('line_total_amount')

    @total_amount.setter
    def total_amount(self, value):
        pass
