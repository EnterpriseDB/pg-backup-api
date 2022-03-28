#!/bin/bash

# Package metadata is defined here
DESCRIPTION="An HTTP API for interacting with Postgres backups\n\
Postgres backup API (pg-backup-api) is an open-source tool for\n\
interacting with Postgres backups via JSON over HTTP."
LICENSE="GPLv3"
URL="https://github.com/EnterpriseDB/pg-backup-api"
VENDOR="EnterpriseDB <barman@enterprisedb.com>"

PKG_TYPE=$1
shift
while [[ $# -gt 0 ]]; do
  case $1 in
    --python)
      PYTHON_VERSION=$2
      shift
      shift
      ;;
    --debug)
      IS_DBG=$1
      shift
      ;;
    --platform-flavour)
      PLATFORM_FLAVOUR=$2
      shift
      shift
      ;;
    --platform-version)
      PLATFORM_VERSION=$2
      shift
      shift
      ;;
    *)
      RELEASE_VERSION=$1
      shift
      ;;
  esac
done

RELEASE_VERSION=${RELEASE_VERSION:-"1"}

# Wrap virtualenv on the build machine so that it is forced to use a specific
# python executable. This ensures that FPM packages for the required version
# of python.
if [ ! -z "$PYTHON_VERSION" ]; then
    cat << EOF > /usr/local/bin/virtualenv
#!/bin/bash
/usr/bin/virtualenv -p /usr/bin/python${PYTHON_VERSION} "\$@"
EOF
    chmod 750 /usr/local/bin/virtualenv
    venv_dir="${HOME}/.fpm-venv-${PYTHON_VERSION}"
    # We must also create and source a venv before invoking FPM so that it
    # uses the correct python version when building the package.
    virtualenv $venv_dir
    . /${venv_dir}/bin/activate
    pip install python-dateutil
    pip install jinja2
    pip install pyyaml
    pip install virtualenv-tools3
fi

if [ "$PKG_TYPE" = "--help" ]; then
    echo "Usage: ./pkg.sh {deb or rpm} [opt: --debug]"
    echo "deb/rpm is case sensitive; chooses which package file type to generate"
    echo "--debug sets fpm's --verbose and --debug flags"
    exit 0
fi

if [ "$PKG_TYPE" = "deb" ]
then
    extra_opts="--deb-systemd ../packaging/build/etc/systemd/system/pg-backup-api.service \
                --deb-systemd-enable"
elif [ "$PKG_TYPE" = "rpm" ]
then
    extra_opts="--virtualenv-other-files-dir ../packaging/build \
                --directories /usr/bin/pgbapi-venv"
else
    echo "Valid package types are rpm or deb."
    exit 1
fi

# For most platforms we can depend on the default python3 package
PYTHON_PACKAGE_DEP="python3"
if [ "$PLATFORM_FLAVOUR" = "sles" ] && [ "$PLATFORM_VERSION" = "12" ]
then
    # For SLES 12 the default python 3 is 3.4 so we must specify 3.6
    PYTHON_PACKAGE_DEP="python36"
fi

if [ "$IS_DBG" = "--debug" ]
then
    DBG_SETTINGS="--verbose --debug"
else
    DBG_SETTINGS=""
fi

cd ../pg_backup_api

VERSION=`cat version.txt`

echo "Generating...\n"

# The --description arg below is a workaround for the handling of newlines in
# fpm which doesn't quite work as expected.
# See https://github.com/jordansissel/fpm/issues/1468 for more information.
fpm $DBG_SETTINGS \
    -s virtualenv \
    -t $PKG_TYPE \
    -d "barman > 2.16" \
    -d $PYTHON_PACKAGE_DEP \
    -p ../packaging \
    -n pg-backup-api \
    -v $VERSION \
    --prefix /usr/bin/pgbapi-venv \
    --after-install ../packaging/after-install.sh \
    --before-remove ../packaging/before-remove-$PKG_TYPE.sh \
    --virtualenv-setup-install \
    --iteration $RELEASE_VERSION \
    --description "$(printf "$DESCRIPTION")" \
    --$PKG_TYPE-changelog ../packaging/changelogs/$PKG_TYPE.changelog \
    --license "$LICENSE" \
    --url "$URL" \
    --vendor "$VENDOR" \
    $extra_opts \
    ./requirements.txt
