#!/usr/bin/env python

""" Determine the package version string from news.yml. """

import yaml

path_to_news = "../pg_backup_api/news.yml"

with open(path_to_news, "r") as fh:
    news = yaml.safe_load(fh)

latest_release = news["pg-backup-api release notes"][0]
version = latest_release["version"]
revision = "iteration" in latest_release and latest_release["iteration"] or "1"

print(f"{version}-{revision}")
