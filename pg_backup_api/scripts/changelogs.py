#!/usr/bin/env python3
#  © Copyright EnterpriseDB UK Limited 2021-2023 - All rights reserved.
#
"""
Generate news.md from a source yaml file using Jinja templates.

Based on @matthbakeredb's TPAExec prototype.

The SOURCE_FILE should be a yaml file in the following format:

- version: "VERSION"
  date: "DATE_IN_ISO8601_FORMAT"
  changes:
    Notable changes:             # Optional
      - "CHANGE_DESCRIPTION"
    Minor changes:               # Optional
      - "CHANGE_DESCRIPTION"
    Bugfixes:                    # Optional
      - "CHANGE_DESCRIPTION"

"""

import os
import textwrap

import yaml
from dateutil import parser
from jinja2 import Environment

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
SOURCE = "news.yml"
TEMPLATES = [
    os.path.join(TEMPLATE_DIR, "news.md.jinja2"),
]


def format_line(line, width, initial_indent, subsequent_indent):
    wrapped = textwrap.wrap(
        line.replace("\n", " "),
        width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
    )
    return "\n".join(wrapped)


def render(template, data):
    env = Environment()
    env.globals.update(format_line=format_line, date_parser=parser.parse)
    env.trim_blocks = True
    env.lstrip_blocks = True
    with open(template) as fh:
        return env.from_string(fh.read()).render(data=data)


def read_data(file_name):
    with open(file_name) as fh:
        return yaml.safe_load(fh)


def write_data(file_name, data):
    with open(file_name, "w+") as fh:
        fh.write(data)


def main():
    data = read_data(SOURCE)
    for template in TEMPLATES:
        write_data(
            template.partition(".jinja2")[0],
            render(template, data),
        )


if __name__ == "__main__":
    main()
