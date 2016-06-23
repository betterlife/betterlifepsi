"""Change organization model to isolate tree

Revision ID: 208ffbb0eb3e
Revises: eaf708894c1d
Create Date: 2016-06-01 22:16:10.260657

"""

# revision identifiers, used by Alembic.
revision = '208ffbb0eb3e'
down_revision = 'eaf708894c1d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint(u'organization_parent_id_fkey', 'organization', type_='foreignkey')
    op.drop_column('organization', 'parent_id')
    # TODO Currently this migration script only works for one organization.
    op.add_column('organization', sa.Column('lft', sa.Integer(), nullable=False, server_default='1', unique=False))
    op.add_column('organization', sa.Column('rgt', sa.Integer(), nullable=False, server_default='2', unique=False))
    op.alter_column('organization', 'lft', server_default=None)
    op.alter_column('organization', 'rgt', server_default=None)


def downgrade():
    op.add_column('organization', sa.Column('parent_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(u'organization_parent_id_fkey', 'organization', 'organization', ['parent_id'], ['id'])
    op.drop_column('organization', 'lft')
    op.drop_column('organization', 'rgt')
