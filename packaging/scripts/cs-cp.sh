#!/bin/bash

# Copy all packages matching supplied version from ibm-dev to edb

# Usage: ./cs-cp.sh 0.1.0-1

export CLOUDSMITH_API_KEY=$(grep api_key ~/.cloudsmith/credentials.ini | cut -d '=' -f 2)
export CLOUDSMITH_TOKEN=$(grep token ~/.cloudsmith/credentials.ini | cut -d '=' -f 2)

package_version=$1
source_repo="ibm-dev"
target_repo="edb"

package_slugs=$(\
  cloudsmith ls pkgs enterprisedb/ibm-dev \
    -q "filename:pg-backup-api*$package_version" -F json \
    | jq -r '.data[].slug'
)

for package in $package_slugs
do
  cloudsmith cp enterprisedb/$source_repo/$package $target_repo
done
