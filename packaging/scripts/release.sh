#!/bin/bash

# Usage: ./release.sh 0.1.0 1

set -e

CHANGELOGS_PATH="changelogs"
PG_BACKUP_API_PATH="../pg_backup_api"
SCRIPTS_PATH="scripts"
TEMPLATES_PATH="templates"
WORKFLOW_PATH="../.github/workflows"

# Read version and iteration from news.yml
full_version=$($SCRIPTS_PATH/get_package_version.py)
version=$(echo $full_version | cut -d '-' -f 1)
revision=$(echo $full_version | cut -d '-' -f 2)

# Set RELEASE_VERSION in the GitHub workflow
sed -i -e "s/RELEASE_VERSION: \"[0-9]\+\"/RELEASE_VERSION: \"$revision\"/" \
    $WORKFLOW_PATH/publish-to-cloudsmith.yml

# Set version.txt
echo $version > $PG_BACKUP_API_PATH/version.txt

# Generate updated changelogs and news and move files into place
$SCRIPTS_PATH/changelogs.py
mv $TEMPLATES_PATH/rpm.changelog $TEMPLATES_PATH/deb.changelog $CHANGELOGS_PATH
mv $TEMPLATES_PATH/news.md $PG_BACKUP_API_PATH

# Commit the changes
git commit -a -m "Prepare release $full_version"

# Tell the user what to do next
echo "Changes for release $full_version have been committed.
Please review the commit, push the changes to a branch and make a PR.
Once merged please tag the \"main\" branch with: release/$full_version."
