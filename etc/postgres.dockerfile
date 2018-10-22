FROM postgres:9.6
COPY bin/db_init.sh /docker-entrypoint-initdb.d/db_init.sh
