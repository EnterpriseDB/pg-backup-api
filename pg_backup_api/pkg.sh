#!/bin/sh


PKG_TYPE=$1

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

fpm $DBG_SETTINGS \
    -s virtualenv \
    -t $PKG_TYPE \
    -n pg-backup-api \
    --virtualenv-setup-install \
    ./requirements.txt

