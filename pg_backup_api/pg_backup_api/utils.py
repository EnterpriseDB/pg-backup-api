# -*- coding: utf-8 -*-
# © Copyright EnterpriseDB UK Limited 2021-2023
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

from logging.config import dictConfig

from flask import Flask

import barman
from barman import config

API_CONFIG = {"supported_options": ("remote_ssh_command",)}

CONFIG_FILENAME = "/etc/barman.conf"
LOG_FILENAME = "/var/log/barman/barman-api.log"


def create_app():
    """
    Create the connexion app with the required API.
    """
    return Flask("Postgres Backup API")


def load_barman_config():
    """
    Load the Barman config into barman.__config__.
    """
    cfg = config.Config(CONFIG_FILENAME)
    barman.__config__ = cfg
    cfg.load_configuration_files_directory()


def setup_logging():
    """
    Configure logging.
    """
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s:%(module)s: %(message)s",
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.FileHandler",
                    "filename": LOG_FILENAME,
                    "formatter": "default",
                }
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
            "disable_existing_loggers": False,
        }
    )


def get_server_by_name(server_name):
    servers = barman.__config__.server_names()
    for server in servers:
        conf = barman.__config__.get_server(server)
        if server == server_name:
            return conf
