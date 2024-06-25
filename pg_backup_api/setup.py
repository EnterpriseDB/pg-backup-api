# -*- coding: utf-8 -*-
# © Copyright EnterpriseDB UK Limited 2021-2024 - All rights reserved.
#
# This file is part of Postgres Backup API.
#
# Postgres Backup API is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Postgres Backup API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Postgres Backup API.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

NAME = "pg-backup-api"

with open("./version.txt", "r") as f:
    VERSION = f.readline().rstrip()

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["barman>=2.19,<4.0.0", "Flask>=0.10.1,<3.0.0",
            "requests>=2.0.0,<3.0.0"]

setup(
    name=NAME,
    version=VERSION,
    description="Postgres Backup REST API",
    author="EnterpriseDB",
    author_email="barman@enterprisedb.com",
    url="http://www.pgbarman.org/",
    keywords=["Postgres Backup REST API"],
    python_requires=">=3.6",
    install_requires=REQUIRES,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    entry_points={
        "console_scripts": ["pg-backup-api=pg_backup_api.__main__:main"],
    },
    license="GPL-3.0",
    long_description="""\
    A server that provides an HTTP API to interact with Postgres backups
    """,
)
