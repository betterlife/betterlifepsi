# encoding: utf-8

from app import const
from app.database import DbInfo
from app.models.data_security_mixin import DataSecurityMixin
from sqlalchemy import Column, Integer, ForeignKey, String, Date, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from app.utils import date_util

db = DbInfo.get_db()


class Customer(db.Model, DataSecurityMixin):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(32), unique=False, nullable=True)
    last_name = Column(String(32), unique=False, nullable=True)
    mobile_phone = Column(String(32), unique=False, nullable=True)
    email = Column(String(64))
    address = Column(String(64), unique=False, nullable=True)
    birthday = Column(Date, nullable=True)
    join_date = Column(Date, nullable=False)
    points = Column(Integer, nullable=False)

    join_channel_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    join_channel = relationship('EnumValues', foreign_keys=[join_channel_id])

    level_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    level = relationship('EnumValues', foreign_keys=[level_id])

    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])

    @hybrid_property
    def member_age(self):
        return int(date_util.num_years(self.join_date))

    @member_age.setter
    def member_age(self, val):
        pass

    @member_age.expression
    def member_age(self):
        """
        Being used in the UI sorting and filtering
        :return:member age
        """
        return func.date_part("year", func.age(self.join_date)).label("member_age")

    @hybrid_property
    def name(self):
        connect = ''
        if str(self.last_name).isalpha() and str(self.first_name).isalpha():
            connect = ' '
        return self.last_name + connect + self.first_name

    @name.setter
    def name(self, value):
        pass

    @hybrid_property
    def total_spent(self):
        orders = self.sales_orders
        t = 0
        for order in orders:
            t += order.actual_amount
        return t

    @total_spent.setter
    def total_spent(self, val):
        pass

    @total_spent.expression
    def total_spent(self):
        from app.models.sales_order import SalesOrder, SalesOrderLine
        return (select([func.sum(SalesOrderLine.quantity * SalesOrderLine.unit_price)])
                .where(SalesOrder.id == SalesOrderLine.sales_order_id)
                .where(self.id == SalesOrder.customer_id)
                .label('total_spent'))

    @staticmethod
    def join_channel_filter():
        from app.models.enum_values import EnumValues
        return EnumValues.type_filter(const.CUSTOMER_JOIN_CHANNEL_KEY)

    @staticmethod
    def level_filter():
        from app.models.enum_values import EnumValues
        return EnumValues.type_filter(const.CUSTOMER_LEVEL_KEY)

    def __repr__(self):
        return self.name + ' - ' + self.level.display
