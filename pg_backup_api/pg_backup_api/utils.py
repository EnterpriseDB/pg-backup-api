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

"""
Utility functions and constants used through pg-backup-api code.

:var CONFIG_FILENAME: path to the main Barman configuration file.
:var LOG_FILENAME: path to the file where pg-backup-api logs its messages.
"""
from logging.config import dictConfig
from typing import Optional, TYPE_CHECKING

from flask import Flask

import barman
from barman import config
from barman.infofile import BackupInfo


if TYPE_CHECKING:  # pragma: no cover
    import flask.app
    from barman.config import Config as BarmanConfig, ServerConfig
    import barman.server


CONFIG_FILENAME = "/etc/barman.conf"
LOG_FILENAME = "/var/log/barman/barman-api.log"


def create_app() -> 'flask.app.Flask':
    """
    Create the connexion app with the required API.

    :return: flask application instance with name ``Postgres Backup API``.
    """
    return Flask("Postgres Backup API")


def load_barman_config() -> None:
    """
    Load the Barman config into :data:`barman.__config__`.

    Source Barman config is retrieved from file :data:`CONFIG_FILE_NAME`.
    """
    cfg = config.Config(CONFIG_FILENAME)
    barman.__config__ = cfg
    cfg.load_configuration_files_directory()


def setup_logging_for_wsgi_server() -> None:
    """
    Configure logging.

    Log records with level :data:`logging.INFO` or higher to file
    :data:`LOG_FILENAME`.
    """
    log_format = "[%(asctime)s] %(levelname)s:%(module)s: %(message)s"
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": log_format,
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


def get_server_by_name(server_name: str) -> Optional['ServerConfig']:
    """
    Get configuration of a Barman server based on the *server_name*.

    :param server_name: name of the server which we want configuration from.
    :return: configuration of Barman server *server_name* if that server
        exists, ``None`` otherwise.
    """
    if TYPE_CHECKING:  # pragma: no cover
        assert isinstance(barman.__config__, BarmanConfig)

    for server in barman.__config__.server_names():  # pyright: ignore
        conf = barman.__config__.get_server(server)
        if server == server_name:
            return conf


def parse_backup_id(server: barman.server.Server,
                    backup_id: str) -> Optional[BackupInfo]:
    """
    Get backup with ID *backup_id* from *server.

    :param server: server from which to get a backup.
    :param backup_id: ID of the backup to be retrieved. It accepts a few
        aliases:

        * ``latest``/``last``: to get the latest backup;
        * ``oldest``/``first``: to get the oldest backup;
        * ``last-failed``: to get the last failed backup.

    :return: information about the backup, if *backup_id* can be satisfied,
        ``None`` otherwise.
    """
    parsed_backup_id = backup_id

    if backup_id in ("latest", "last"):
        parsed_backup_id = server.get_last_backup_id()
    elif backup_id in ("oldest", "first"):
        parsed_backup_id = server.get_first_backup_id()
    elif backup_id in ("last-failed"):
        parsed_backup_id = server.get_last_backup_id([BackupInfo.FAILED])

    return server.get_backup(parsed_backup_id)
