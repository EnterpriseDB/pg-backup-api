#!/bin/sh

# clean up __pycache__ files so they don't interfere with uninstallation

cd /usr/bin/pgbapi-venv
find . -type d -name __pycache__ -exec rm -r {} \+

# clean up executable that we moved on install
cd ..
rm pg-backup-api

