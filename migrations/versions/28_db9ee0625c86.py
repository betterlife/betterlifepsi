"""Add purchase_price_view and product_inventory_view role

Revision ID: db9ee0625c86
Revises: 7868d8cd502d
Create Date: 2016-08-18 00:35:48.257255

"""

# revision identifiers, used by Alembic.
revision = 'db9ee0625c86'
down_revision = '7868d8cd502d'

from alembic import op

def upgrade():
    from sqlalchemy.sql import text
    op.get_bind().execute(text("INSERT INTO role (name, description) VALUES ('purchase_price_view', 'Purchase Price View');"))
    op.get_bind().execute(text("INSERT INTO role (name, description) VALUES ('product_inventory_view', 'Product Inventory View');"))


def downgrade():
    from sqlalchemy.sql import text
    op.get_bind().execute(text("DELETE FROM role where name ='purchase_price_view'"))
    op.get_bind().execute(text("DELETE FROM role where name ='product_inventory_view'"))
