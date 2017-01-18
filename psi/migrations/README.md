This folder contains all alembic migration for DB schema changes.

Run the manage.py script in app root directory to operate on migrations.

- Show current migration level

    python manage.py db current

- Generate a migration from current model definition to current DB schema:

    python manage.py db migrate

- Apply migration

    python manage.py db upgrade

-  Revert to a previous version

    python manage.py db downgrade

