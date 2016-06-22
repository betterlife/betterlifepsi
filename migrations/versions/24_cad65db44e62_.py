""" Add default value for lft and rgt column of organization

Revision ID: cad65db44e62
Revises: 1e9c8b5db3a7
Create Date: 2016-06-16 07:39:00.846930

"""

# revision identifiers, used by Alembic.
revision = 'cad65db44e62'
down_revision = '1e9c8b5db3a7'

from alembic import op


def upgrade():
    op.alter_column('organization', 'lft', server_default='0')
    op.alter_column('organization', 'rgt', server_default='0')


def downgrade():
    op.alter_column('organization', 'lft', server_default="1")
    op.alter_column('organization', 'rgt', server_default="2")
