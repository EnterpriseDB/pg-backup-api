#!/usr/bin/env python

"""Determine the version string from news.yml."""

import yaml

path_to_news = "../pg_backup_api/news.yml"

with open(path_to_news, "r") as fh:
    news = yaml.safe_load(fh)

latest_release = news["pg-backup-api release notes"][0]
version = latest_release["version"]

print(f"{version}")
