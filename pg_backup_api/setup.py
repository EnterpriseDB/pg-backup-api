# -*- coding: utf-8 -*-
# © Copyright EnterpriseDB UK Limited 2013-2021
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

import sys
from setuptools import setup, find_packages

NAME = "pg_backup_api"
VERSION = "0.1.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "barman>2.16",
    "connexion>=2.0.2",
    "python_dateutil>=2.6.0",
    "Jinja2 <3.0, >=2.10.1"
]

setup(
    name=NAME,
    version=VERSION,
    description="Postgres Backup REST API",
    author="EnterpriseDB",
    author_email="barman@enterprisedb.com",
    url="http://www.pgbarman.org/",
    keywords=["OpenAPI", "Postgres Backup REST API"],
    python_requires='>=3.6',
    install_requires=REQUIRES,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    entry_points={
        'console_scripts': ['pg-backup-api=pg_backup_api.run:main']},
    license="GPL-3.0",
    long_description="""\
    A server that provides an HTTP API to interact with Postgres backups
    """
)

