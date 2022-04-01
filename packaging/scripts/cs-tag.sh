#!/bin/bash

# Tag all pg-backup-api packages in the edb repo matching the supplied version
# with the supplied tag

# Usage: ./cs-tag.sh 0.1.0-1 production

export CLOUDSMITH_API_KEY=$(grep api_key ~/.cloudsmith/credentials.ini | cut -d '=' -f 2)
export CLOUDSMITH_TOKEN=$(grep token ~/.cloudsmith/credentials.ini | cut -d '=' -f 2)

repo="edb"
package_version=$1
tag=$2

package_slugs=$(\
  cloudsmith ls pkgs enterprisedb/$repo \
    -q "filename:pg-backup-api*$package_version" -F json \
    | jq -r '.data[].slug'
)

for package in $package_slugs
do
  cloudsmith tag add enterprisedb/$repo/$package production
done
