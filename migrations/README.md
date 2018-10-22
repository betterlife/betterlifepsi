This folder contains all alembic migration for DB schema changes.

Run the flask utility script in app root directory to operate on migrations.

- Show current migration level

    flask db current

- Generate a migration from current model definition to current DB schema:

    flask db migrate

- Apply migration

    flask db upgrade

-  Revert to a previous version

    flask db downgrade

