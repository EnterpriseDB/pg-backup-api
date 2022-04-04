#!/bin/bash

# Usage: ./release.sh 0.1.0 1

set -e

PG_BACKUP_API_PATH="./"
SCRIPTS_PATH="scripts"
TEMPLATES_PATH="$SCRIPTS_PATH/templates"

# Read version and iteration from news.yml
version=$($SCRIPTS_PATH/get_version.py)

# Set version.txt
echo $version > $PG_BACKUP_API_PATH/version.txt

# Generate updated changelogs and news and move files into place
$SCRIPTS_PATH/changelogs.py
mv $TEMPLATES_PATH/news.md $PG_BACKUP_API_PATH

# Commit the changes
git commit -a -m "Prepare release $version"

# Tell the user what to do next
echo "Changes for release $version have been committed.
Please review the commit, push the changes to a branch and make a PR.
Once merged please tag the \"main\" branch with: release/$version and push the tag."
