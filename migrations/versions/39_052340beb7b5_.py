""" Generate mnemonic for all existing supplier, customer and product

Revision ID: 052340beb7b5
Revises: 3c66f436a5be
Create Date: 2017-05-07 11:57:28.076668

"""

# revision identifiers, used by Alembic.
revision = '052340beb7b5'
down_revision = '3c66f436a5be'

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text


def upgrade():
    # Follow line is needed to persist all existing migration to DB and avoid
    # tests to complain supplier, product and customer tables does not exist
    op.get_bind().execute(text("COMMIT;"))
    set_mnemonic_for_all(fields=['id', 'name'], obj_type="supplier")
    set_mnemonic_for_all(fields=['id', 'name'], obj_type="product")
    set_mnemonic_for_all(fields=['id', 'first_name', 'last_name'], obj_type="customer")
    op.get_bind().execute(text("COMMIT;"))
    # ### end Alembic commands ###


def set_mnemonic_for_all(fields, obj_type):
    join = ",".join(fields) if len(fields) > 0 else fields[0]
    objs = op.get_bind().execute(text("select {0} from {1}".format(join, obj_type))).fetchall()
    for s in objs:
        from psi.app.utils.format_util import get_pinyin_first_letters
        v = ''
        s_id = s[0]
        for i in range(1, len(fields)):
            v += s[i]
        m = get_pinyin_first_letters(v)
        op.get_bind().execute(text("update {0} set mnemonic = '{1}' where id={2}".format(obj_type, m, s_id)))


def downgrade():
    op.get_bind().execute(text("update supplier set mnemonic = '';"))
    op.get_bind().execute(text("update product set mnemonic = '';"))
    op.get_bind().execute(text("update customer set mnemonic = '';"))
