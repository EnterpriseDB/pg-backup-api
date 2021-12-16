#!/bin/sh


PKG_TYPE=$1

if [ "$PKG_TYPE" != "deb" ] && [ "$PKG_TYPE" != "rpm" ]
then
    echo "Valid package types are rpm or deb."
    exit 1
fi

fpm --verbose --debug --debug-workspace \
    -s virtualenv \
    -t $PKG_TYPE \
    -n pg-backup-api \
    --virtualenv-setup-install \
    ./requirements.txt

