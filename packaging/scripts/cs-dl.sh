#!/bin/bash

# A convenience script to download all pg-backup-api packages in a given repo

# Usage: ./cs-dl.sh ibm-dev

export CLOUDSMITH_API_KEY=$(grep api_key ~/.cloudsmith/credentials.ini | cut -d '=' -f 2)
export CLOUDSMITH_TOKEN=$(grep token ~/.cloudsmith/credentials.ini | cut -d '=' -f 2)

repo=$1
package_version=$2

urls=$(\
  cloudsmith ls pkgs enterprisedb/$repo \
    -q "filename:pg-backup-api*$package_version" -F json \
    | jq -r '.data[].files[].cdn_url'
)

for url in $urls
do
  curl -u token:$CLOUDSMITH_TOKEN -1Lf -O $url
done
