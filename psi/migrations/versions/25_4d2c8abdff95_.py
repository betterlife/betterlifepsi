"""Change Organization lft and rgt to unique

Revision ID: 4d2c8abdff95
Revises: 0051eed6ee5d
Create Date: 2016-07-16 01:02:07.714519

"""

# revision identifiers, used by Alembic.
revision = '4d2c8abdff95'
down_revision = 'cad65db44e62'

from alembic import op


def upgrade():
    op.create_unique_constraint(None, 'organization', ['lft'])
    op.create_unique_constraint(None, 'organization', ['rgt'])


def downgrade():
    op.drop_constraint(None, 'organization', type_='unique')
    op.drop_constraint(None, 'organization', type_='unique')
