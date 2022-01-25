#!/bin/sh


PKG_TYPE=$1

if [ "$PKG_TYPE" = "--help" ]; then
    echo "Usage: ./pkg.sh {deb or rpm} [opt: --debug]"
    echo "deb/rpm is case sensitive; chooses which package file type to generate"
    echo "--debug sets fpm's --verbose and --debug flags"
    exit 0
fi

if [ "$PKG_TYPE" != "deb" ] && [ "$PKG_TYPE" != "rpm" ]
then
    echo "Valid package types are rpm or deb."
    exit 1
fi

IS_DBG=$2

if [ "$IS_DBG" = "--debug" ]
then
    DBG_SETTINGS="--verbose --debug"
else
    DBG_SETTINGS=""
fi

cd ../pg_backup_api

VERSION=`cat version.txt`

echo "Generating...\n"

fpm $DBG_SETTINGS \
    -s virtualenv \
    -t $PKG_TYPE \
    -d "barman > 2.16" \
    -p ../packaging \
    -n pg-backup-api \
    -v $VERSION \
    --prefix /usr/bin/pgbapi-venv \
    --after-install ../packaging/after-install.sh \
    --before-remove ../packaging/before-remove.sh \
    --deb-systemd ../packaging/pg-backup-api.service \
    --virtualenv-setup-install \
    ./requirements.txt
