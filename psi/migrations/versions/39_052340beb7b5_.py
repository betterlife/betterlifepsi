""" Generate mnemonic for all existing supplier, customer and product

Revision ID: 052340beb7b5
Revises: 3c66f436a5be
Create Date: 2017-05-07 11:57:28.076668

"""

# revision identifiers, used by Alembic.
revision = '052340beb7b5'
down_revision = '3c66f436a5be'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text



def upgrade():
    from psi.app.models import Supplier, Product, Customer
    from psi.app.service import Info
    # Follow line is needed to persist all existing migration to DB and avoid
    # tests to complain supplier, product and customer tables does not exist
    op.get_bind().execute(text("COMMIT;"))
    db = Info.get_db()
    set_mnemonic_for_all(db, obj_type=Supplier)
    set_mnemonic_for_all(db, obj_type=Product)
    set_mnemonic_for_all(db, obj_type=Customer)
    db.session.commit()
    # ### end Alembic commands ###


def set_mnemonic_for_all(db, obj_type):
    objs = db.session.query(obj_type).all()
    for s in objs:
        from psi.app.utils import get_pinyin_first_letters
        v = s.get_value_for_mnemonic() if hasattr(s, 'get_value_for_mnemonic') else s.name
        m = get_pinyin_first_letters(v)
        s.mnemonic = m
        db.session.add(s)


def downgrade():
    op.get_bind().execute(text("update supplier set mnemonic = '';"))
    op.get_bind().execute(text("update product set mnemonic = '';"))
    op.get_bind().execute(text("update customer set mnemonic = '';"))
