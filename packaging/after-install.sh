#!/bin/sh

# move the pg-backup-api executable from the pgbapi virtualenv
# into /usr/bin to put it on the PATH

mv /usr/bin/pgbapi-venv/bin/pg-backup-api /usr/bin

# make sure the venv is on the PYTHONPATH
VENV_SITE_PACKAGES_DIR=$(find /usr/bin/pgbapi-venv -name site-packages -type d)
EGG_DIR=$(find $VENV_SITE_PACKAGES_DIR -name pg_backup_api -type d)  # so this script doesn't have to know the pgbapi version
export PYTHONPATH="$VENV_SITE_PACKAGES_DIR:$EGG_DIR:$PYTHONPATH"


# set up the log file TODO match up with config settings once that capability is added
touch /var/log/barman/barman-api.log
chown barman:barman /var/log/barman/barman-api.log

