# -*- coding: utf-8 -*-
# © Copyright EnterpriseDB UK Limited 2021-2022
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

import connexion

import barman
from barman import config

from pg_backup_api.openapi_server import encoder

CONFIG_FILENAME = "/etc/barman.conf"


def create_app():
    """
    Create the connexion app with the required API.
    """
    app = connexion.App(__name__, specification_dir="./spec/")
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api(
        "pg_backup_api.yaml",
        arguments={"title": "Postgres Backup API"},
        pythonic_params=True,
    )
    return app


def load_barman_config():
    """
    Load the Barman config into barman.__config__.
    """
    cfg = config.Config(CONFIG_FILENAME)
    barman.__config__ = cfg
    cfg.load_configuration_files_directory()
