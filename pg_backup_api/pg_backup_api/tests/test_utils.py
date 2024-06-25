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

"""Unit tests for utilitary functions."""
from unittest.mock import MagicMock, patch, call

from barman.infofile import BackupInfo
import pytest

from pg_backup_api.utils import (create_app, load_barman_config,
                                 setup_logging_for_wsgi_server,
                                 get_server_by_name, parse_backup_id)


@patch("pg_backup_api.utils.Flask")
def test_create_app(mock_flask):
    """Test :func:`create_app`.

    Ensure the :class:`Flask` object is created as expected.
    """
    assert create_app() == mock_flask.return_value

    mock_flask.assert_called_once_with("Postgres Backup API")


@patch("pg_backup_api.utils.config.Config")
@patch("barman.__config__")
def test_load_barman_config(mock_global_config, mock_config):
    """Test :func:`load_barman_config`.

    Ensure Barman configuration is loaded as expected.
    """
    assert load_barman_config() is None

    mock_config.assert_called_once_with("/etc/barman.conf")
    mock_global_config == mock_config.return_value
    mock_load = mock_config.return_value.load_configuration_files_directory
    mock_load.assert_called_once_with()


@patch("pg_backup_api.utils.dictConfig")
def test_setup_logging_for_wsgi_server(mock_dict_config):
    """Test :func:`setup_logging_for_wsgi_server`.

    Ensure :meth:`logging.config.dictConfig` is called as expected.
    """
    assert setup_logging_for_wsgi_server() is None

    log_format = "[%(asctime)s] %(levelname)s:%(module)s: %(message)s"
    expected = {
        "version": 1,
        "formatters": {
            "default": {
                "format": log_format,
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.FileHandler",
                "filename": "/var/log/barman/barman-api.log",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
        "disable_existing_loggers": False,
    }
    mock_dict_config.assert_called_once_with(expected)


@patch("barman.__config__")
def test_get_server_by_name_not_found(mock_config):
    """Test :func:`get_server_by_name`.

    Ensure ``None`` is returned if the server could not be found.
    """
    mock_server_names = mock_config.server_names
    mock_server_names.return_value = ["SERVER_1", "SERVER_2", "SERVER_3"]
    mock_get_server = mock_config.get_server

    assert get_server_by_name("SERVER_4") is None

    mock_server_names.assert_called_once_with()
    mock_get_server.assert_has_calls([
        call("SERVER_1"),
        call("SERVER_2"),
        call("SERVER_3"),
    ])


@patch("barman.__config__")
def test_get_server_by_name_ok(mock_config):
    """Test :func:`get_server_by_name`.

    Ensure a server is returned if the server could be found.
    """
    mock_server_names = mock_config.server_names
    mock_server_names.return_value = ["SERVER_1", "SERVER_2", "SERVER_3"]
    mock_get_server = mock_config.get_server

    assert get_server_by_name("SERVER_2") == mock_get_server.return_value

    mock_server_names.assert_called_once_with()
    mock_get_server.assert_has_calls([
        call("SERVER_1"),
        call("SERVER_2"),
    ])


@pytest.mark.parametrize("backup_id", ["latest", "last"])
def test_parse_backup_id_latest(backup_id):
    """Test :func:`parse_backup_id`.

    Ensure :meth:`barman.server.Server.get_last_backup_id()` is called when
    backup ID is either ``latest`` or ``last``, then the corresponding backup
    is returned.
    """
    mock_server = MagicMock()

    expected = mock_server.get_backup.return_value
    assert parse_backup_id(mock_server, backup_id) == expected

    mock_server.get_last_backup_id.assert_called_once_with()
    mock_server.get_first_backup_id.assert_not_called()
    expected = mock_server.get_last_backup_id.return_value
    mock_server.get_backup.assert_called_once_with(expected)


@pytest.mark.parametrize("backup_id", ["oldest", "first"])
def test_parse_backup_id_first(backup_id):
    """Test :func:`parse_backup_id`.

    Ensure :meth:`barman.server.Server.get_first_backup_id()` is called when
    backup ID is either ``oldest`` or ``first``, then the corresponding backup
    is returned.
    """
    mock_server = MagicMock()

    expected = mock_server.get_backup.return_value
    assert parse_backup_id(mock_server, backup_id) == expected

    mock_server.get_last_backup_id.assert_not_called()
    mock_server.get_first_backup_id.assert_called_once_with()
    expected = mock_server.get_first_backup_id.return_value
    mock_server.get_backup.assert_called_once_with(expected)


def test_parse_backup_id_last_failed():
    """Test :func:`parse_backup_id`.

    Ensure :meth:`barman.server.Server.get_last_backup_id()` is called when
    backup ID is ``last-failed``, then the corresponding backup is returned.
    """
    backup_id = "last-failed"

    mock_server = MagicMock()

    expected = mock_server.get_backup.return_value
    assert parse_backup_id(mock_server, backup_id) == expected

    mock_server.get_last_backup_id.assert_called_once_with([BackupInfo.FAILED])
    mock_server.get_first_backup_id.assert_not_called()
    expected = mock_server.get_last_backup_id.return_value
    mock_server.get_backup.assert_called_once_with(expected)


def test_parse_backup_id_random():
    """Test :func:`parse_backup_id`.

    Ensure only :meth:`barman.server.Server.get_backup()` is called.
    """
    backup_id = "random"

    mock_server = MagicMock()

    expected = mock_server.get_backup.return_value
    assert parse_backup_id(mock_server, backup_id) == expected

    mock_server.get_last_backup_id.assert_not_called()
    mock_server.get_first_backup_id.assert_not_called()
    mock_server.get_backup.assert_called_once_with(backup_id)
