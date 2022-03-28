#!/usr/bin/env python

"""
Simple script to generate changelogs in either rpm or deb format.

    ./generate-changelog.py SOURCE_FILE rpm|deb

The SOURCE_FILE should be a yaml file in the following format:

- version: "VERSION"
  iteration: "ITERATION" # (optional, defaults to 1)
  author:
    name: "AUTHOR_NAME"
    email: "AUTHOR_EMAIL"
  release_date: "DATE_IN_ISO8601_FORMAT"
  changes:
    - "CHANGE_DESCRIPTION"
  fixes:
    - "BUGFIX_DESCRIPTION"

Both the `changes` and `fixes` fields are optional.

"""
from re import sub
import sys
import textwrap

import jinja2
import yaml

from dateutil import parser

source = sys.argv[1]
format = sys.argv[2]


def format_line(line, width, initial_indent, subsequent_indent):
    wrapped = textwrap.wrap(
        line.replace("\n", " "),
        width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
    )
    return "\n".join(wrapped)


if format == "rpm":
    raw_template = """* {{ date.strftime("%a %b %d %Y") }} - {{ author["name"] }} <{{ author["email"] }}> {{ version }}-{{ iteration }}
{% for line in lines %}{{ format_line(line, 79, "- ", " "*2) }}
{% endfor %}
"""
elif format == "deb":
    raw_template = """pg-backup-api ({{ version }}-{{ iteration }}) unstable; urgency=low
{% for line in lines %}
{{ format_line(line, 79, "  * ", " "*4) }}
{% endfor %}
 -- {{ author["name"] }} <{{ author["email"] }}>  {{ date.strftime("%a, %-d %b %Y %H:%M:%S %z") }}

"""

with open(source, "r") as raw_changelog:
    changelog = yaml.safe_load(raw_changelog)

env = jinja2.Environment()
template = env.from_string(source=raw_template)

for release in changelog:
    release_date = parser.parse(release["release_date"])
    if "changes" not in release:
        release["changes"] = []
    if "fixes" not in release:
        release["fixes"] = []
    output = template.render(
        author=release["author"],
        date=release_date,
        iteration="iteration" in release and release["iteration"] or 1,
        lines=release["changes"] + release["fixes"],
        version=release["version"],
        format_line=format_line,
    )
    print(output)
