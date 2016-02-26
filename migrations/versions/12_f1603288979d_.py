# coding=utf-8
""" Add more seed data for the system to act correct upon first installation

Revision ID: f1603288979d
Revises: faa0a5506a14
Create Date: 2016-02-26 13:28:52.628110

"""

# revision identifiers, used by Alembic.
revision = 'f1603288979d'
down_revision = 'faa0a5506a14'

from alembic import op
import sqlalchemy as sa


def upgrade():
    from sqlalchemy.sql import text
    enum_values_table = sa.table('enum_values',
                                 sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                                 sa.Column('type_id', sa.Integer(), nullable=True),
                                 sa.Column('code', sa.String(length=32), nullable=True),
                                 sa.Column('display', sa.String(length=64), nullable=False),
                                 sa.ForeignKeyConstraint(['type_id'], ['enum_values.id'], ),
                                 sa.PrimaryKeyConstraint('id'),
                                 sa.UniqueConstraint('code'),
                                 )
    op.bulk_insert(enum_values_table, [
        {'id': 14, 'type_id': 1, 'code': 'INVENTORY_TRANSACTION_TYPE', 'display': u'库存变动类型'},
        {'id': 15, 'type_id': 1, 'code': 'RECEIVING_STATUS', 'display': u'收货单状态'},
        {'id': 16, 'type_id': 1, 'code': 'PURCHASE_ORDER_STATUS', 'display': u'采购单状态'},
        {'id': 17, 'type_id': 1, 'code': 'SHIPPING_STATUS', 'display': u'发货单状态'},
        {'id': 18, 'type_id': 14, 'code': 'PURCHASE_IN', 'display': u'采购入库'},
        {'id': 19, 'type_id': 14, 'code': 'SALES_OUT', 'display': u'销售出库'},
        {'id': 20, 'type_id': 14, 'code': 'INVENTORY_DAMAGED', 'display': u'商品损毁'},
        {'id': 21, 'type_id': 14, 'code': 'INVENTORY_LOST', 'display': u'商品丢失'},
        {'id': 22, 'type_id': 15, 'code': 'RECEIVING_DRAFT', 'display': u'收货单草稿'},
        {'id': 23, 'type_id': 15, 'code': 'RECEIVING_COMPLETE', 'display': u'收货单完成'},
        {'id': 24, 'type_id': 16, 'code': 'PURCHASE_ORDER_DRAFT', 'display': u'草稿'},
        {'id': 25, 'type_id': 16, 'code': 'PURCHASE_ORDER_ISSUED', 'display': u'已发出'},
        {'id': 26, 'type_id': 16, 'code': 'PURCHASE_ORDER_PART_RECEIVED', 'display': u'部分收货'},
        {'id': 27, 'type_id': 16, 'code': 'PURCHASE_ORDER_RECEIVED', 'display': u'收货完成'},
        {'id': 28, 'type_id': 17, 'code': 'SHIPPING_COMPLETE', 'display': u'发货完成'},
    ], multiinsert=False)
    op.get_bind().execute(text("ALTER SEQUENCE enum_values_id_seq RESTART WITH 14;"))


def downgrade():
    pass
