"""Add sales order line detail view for report.

Revision ID: 1e9c8b5db3a7
Revises: 208ffbb0eb3e
Create Date: 2016-06-08 00:34:56.618766

"""

from alembic import op
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '1e9c8b5db3a7'
down_revision = '208ffbb0eb3e'


def upgrade():
    op.get_bind().execute(text("""
        CREATE OR REPLACE VIEW sales_order_detail AS 
        SELECT sol.unit_price AS sales_price, sol.quantity, 
            sol.unit_price * sol.quantity AS sales_amount, p.name AS product_name, 
            p.code AS product_code, p.id AS product_id, p.purchase_price, 
            p.purchase_price * sol.quantity AS purchase_amount, 
            sol.unit_price * sol.quantity - p.purchase_price * sol.quantity - so.logistic_amount AS profit, 
            so.order_date
        FROM sales_order_line sol, product p, sales_order so
        WHERE sol.product_id = p.id AND sol.sales_order_id = so.id;
    """))


def downgrade():
    op.get_bind().execute(text("drop view sales_order_detail;"))
