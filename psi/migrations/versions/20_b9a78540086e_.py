# coding=utf-8
""" Add language and time zone seed data

Revision ID: b9a78540086e
Revises: 93a6e0ee63c9
Create Date: 2016-04-21 22:51:20.019802

"""

# revision identifiers, used by Alembic.
revision = 'b9a78540086e'
down_revision = '93a6e0ee63c9'

from alembic import op


def upgrade():
    from sqlalchemy.sql import text
    op.get_bind().execute(text("INSERT INTO enum_values (type_id, code, display) VALUES (1, 'LANGUAGES', '语言');"))
    op.get_bind().execute(text("INSERT INTO enum_values (type_id, code, display) VALUES ((SELECT id FROM enum_values WHERE code='LANGUAGES'), 'zh_CN', '简体中文');"))
    op.get_bind().execute(text("INSERT INTO enum_values (type_id, code, display) VALUES ((SELECT id FROM enum_values WHERE code='LANGUAGES'), 'en_US', 'English');"))
    op.get_bind().execute(text("INSERT INTO enum_values (type_id, code, display) VALUES (1, 'TIMEZONES', '时区');"))
    op.get_bind().execute(text("INSERT INTO enum_values (type_id, code, display) VALUES ((SELECT id FROM enum_values WHERE code='TIMEZONES'), 'UTC/GMT', 'Greenwich Mean Time');"))
    op.get_bind().execute(text("INSERT INTO enum_values (type_id, code, display) VALUES ((SELECT id FROM enum_values WHERE code='TIMEZONES'), 'CST', '北京时间');"))


def downgrade():
    from sqlalchemy.sql import text
    op.get_bind().execute(text("DELETE FROM enum_values WHERE code = 'en_US';"))
    op.get_bind().execute(text("DELETE FROM enum_values WHERE code = 'zh_CN';"))
    op.get_bind().execute(text("DELETE FROM enum_values WHERE code = 'LANGUAGES';"))
    op.get_bind().execute(text("DELETE FROM enum_values WHERE code = 'UTC/GMT';"))
    op.get_bind().execute(text("DELETE FROM enum_values WHERE code = 'CST';"))
    op.get_bind().execute(text("DELETE FROM enum_values WHERE code = 'TIMEZONES';"))
