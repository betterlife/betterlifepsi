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
                                 )
    res = op.get_bind().execute('SELECT max(id)+1 FROM enum_values')
    results = res.fetchall()
    cm = 14
    for r in results:
        cm = r[0]
    op.bulk_insert(enum_values_table, [
        {'id': cm, 'type_id': 1, 'code': 'INVENTORY_TRANSACTION_TYPE', 'display': u'库存变动类型'},
        {'id': cm + 1, 'type_id': 1, 'code': 'RECEIVING_STATUS', 'display': u'收货单状态'},
        {'id': cm + 2, 'type_id': 1, 'code': 'PURCHASE_ORDER_STATUS', 'display': u'采购单状态'},
        {'id': cm + 3, 'type_id': 1, 'code': 'SHIPPING_STATUS', 'display': u'发货单状态'},
        {'id': cm + 4, 'type_id': cm, 'code': 'PURCHASE_IN', 'display': u'采购入库'},
        {'id': cm + 5, 'type_id': cm, 'code': 'SALES_OUT', 'display': u'销售出库'},
        {'id': cm + 6, 'type_id': cm, 'code': 'INVENTORY_DAMAGED', 'display': u'商品损毁'},
        {'id': cm + 7, 'type_id': cm, 'code': 'INVENTORY_LOST', 'display': u'商品丢失'},
        {'id': cm + 8, 'type_id': cm + 1, 'code': 'RECEIVING_DRAFT', 'display': u'收货单草稿'},
        {'id': cm + 9, 'type_id': cm + 1, 'code': 'RECEIVING_COMPLETE', 'display': u'收货单完成'},
        {'id': cm + 10, 'type_id': cm + 2, 'code': 'PURCHASE_ORDER_DRAFT', 'display': u'草稿'},
        {'id': cm + 11, 'type_id': cm + 2, 'code': 'PURCHASE_ORDER_ISSUED', 'display': u'已发出'},
        {'id': cm + 12, 'type_id': cm + 2, 'code': 'PURCHASE_ORDER_PART_RECEIVED', 'display': u'部分收货'},
        {'id': cm + 13, 'type_id': cm + 2, 'code': 'PURCHASE_ORDER_RECEIVED', 'display': u'收货完成'},
        {'id': cm + 14, 'type_id': cm + 3, 'code': 'SHIPPING_COMPLETE', 'display': u'发货完成'},
    ], multiinsert=False)
    op.get_bind().execute(text("ALTER SEQUENCE enum_values_id_seq RESTART WITH " + str(cm + 15) + ";"))


def downgrade():
    pass
