#!/bin/sh

# move the pg-backup-api executable from the pgbapi virtualenv
# into /usr/bin to put it on the PATH

mv /usr/bin/pgbapi-venv/bin/pg-backup-api /usr/bin

# make sure the venv is on the PYTHONPATH
# TODO check if it's ok that our venv py version is 3.9
EGG_DIR=$(ls /usr/bin/pgbapi-venv/lib/python3.9/site-packages | grep pg_backup_api)  # so this script doesn't have to know the pgbapi version
export PYTHONPATH="/usr/bin/pgbapi-venv/lib/python3.9/site-packages:/usr/bin/pgbapi-venv/lib/python3.9/site-packages/$EGG_DIR:$PYTHONPATH"

