# encoding=utf-8

# encoding: utf-8
import datetime

from app import const
from app.app_provider import AppInfo
from app.models.enum_values import EnumValues
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from utils import date_util

db = AppInfo.get_db()


class Customer(db.Model):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(32), unique=False, nullable=True)
    last_name = Column(String(32), unique=False, nullable=True)
    mobile_phone = Column(String(32), unique=False, nullable=True)
    email = Column(String(64))
    address = Column(String(64), unique=False, nullable=True)
    birthday = Column(Date, nullable=True)
    join_date = Column(DateTime, nullable=False)
    points = Column(Integer, nullable=False)

    join_channel_id = Column(Integer, ForeignKey('enum_values.id'), nullable=True)
    join_channel = relationship('EnumValues', foreign_keys=[join_channel_id])

    level_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    level = relationship('EnumValues', foreign_keys=[level_id])

    @hybrid_property
    def member_age(self):
        return int(date_util.num_years(self.join_date))

    @member_age.setter
    def member_age(self, val):
        pass

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

    @staticmethod
    def join_channel_filter():
        return EnumValues.type_filter(const.CUSTOMER_JOIN_CHANNEL_KEY)

    @staticmethod
    def level_filter():
        return EnumValues.type_filter(const.CUSTOMER_LEVEL_KEY)

    def __repr__(self):
        return self.name + ' - ' + self.level.display
