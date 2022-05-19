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

# This file was autogenerated by OpenAPI Generator.

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from pg_backup_api.openapi_server.models.base_model_ import Model
from pg_backup_api.openapi_server.models.backups_value import BackupsValue
from pg_backup_api.openapi_server.models.server_config import ServerConfig
from pg_backup_api.openapi_server.models.status import Status
from pg_backup_api.openapi_server.models.wals import Wals
from pg_backup_api.openapi_server import util

from pg_backup_api.openapi_server.models.backups_value import BackupsValue  # noqa: E501
from pg_backup_api.openapi_server.models.server_config import ServerConfig  # noqa: E501
from pg_backup_api.openapi_server.models.status import Status  # noqa: E501
from pg_backup_api.openapi_server.models.wals import Wals  # noqa: E501


class DiagnoseOutputServersValue(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, backups=None, config=None, status=None, wals=None):  # noqa: E501
        """DiagnoseOutputServersValue - a model defined in OpenAPI

        :param backups: The backups of this DiagnoseOutputServersValue.  # noqa: E501
        :type backups: Dict[str, BackupsValue]
        :param config: The config of this DiagnoseOutputServersValue.  # noqa: E501
        :type config: ServerConfig
        :param status: The status of this DiagnoseOutputServersValue.  # noqa: E501
        :type status: Status
        :param wals: The wals of this DiagnoseOutputServersValue.  # noqa: E501
        :type wals: Wals
        """
        self.openapi_types = {
            "backups": Dict[str, BackupsValue],
            "config": ServerConfig,
            "status": Status,
            "wals": Wals,
        }

        self.attribute_map = {
            "backups": "backups",
            "config": "config",
            "status": "status",
            "wals": "wals",
        }

        self._backups = backups
        self._config = config
        self._status = status
        self._wals = wals

    @classmethod
    def from_dict(cls, dikt):
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The DiagnoseOutput_servers_value of this DiagnoseOutputServersValue.  # noqa: E501
        :rtype: DiagnoseOutputServersValue
        """
        return util.deserialize_model(dikt, cls)

    @property
    def backups(self):
        """Gets the backups of this DiagnoseOutputServersValue.

        Details of each backup stored by Barman for this server keyed by Backup ID.   # noqa: E501

        :return: The backups of this DiagnoseOutputServersValue.
        :rtype: Dict[str, BackupsValue]
        """
        return self._backups

    @backups.setter
    def backups(self, backups):
        """Sets the backups of this DiagnoseOutputServersValue.

        Details of each backup stored by Barman for this server keyed by Backup ID.   # noqa: E501

        :param backups: The backups of this DiagnoseOutputServersValue.
        :type backups: Dict[str, BackupsValue]
        """
        if backups is None:
            raise ValueError(
                "Invalid value for `backups`, must not be `None`"
            )  # noqa: E501

        self._backups = backups

    @property
    def config(self):
        """Gets the config of this DiagnoseOutputServersValue.


        :return: The config of this DiagnoseOutputServersValue.
        :rtype: ServerConfig
        """
        return self._config

    @config.setter
    def config(self, config):
        """Sets the config of this DiagnoseOutputServersValue.


        :param config: The config of this DiagnoseOutputServersValue.
        :type config: ServerConfig
        """
        if config is None:
            raise ValueError(
                "Invalid value for `config`, must not be `None`"
            )  # noqa: E501

        self._config = config

    @property
    def status(self):
        """Gets the status of this DiagnoseOutputServersValue.


        :return: The status of this DiagnoseOutputServersValue.
        :rtype: Status
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this DiagnoseOutputServersValue.


        :param status: The status of this DiagnoseOutputServersValue.
        :type status: Status
        """
        if status is None:
            raise ValueError(
                "Invalid value for `status`, must not be `None`"
            )  # noqa: E501

        self._status = status

    @property
    def wals(self):
        """Gets the wals of this DiagnoseOutputServersValue.


        :return: The wals of this DiagnoseOutputServersValue.
        :rtype: Wals
        """
        return self._wals

    @wals.setter
    def wals(self, wals):
        """Sets the wals of this DiagnoseOutputServersValue.


        :param wals: The wals of this DiagnoseOutputServersValue.
        :type wals: Wals
        """
        if wals is None:
            raise ValueError(
                "Invalid value for `wals`, must not be `None`"
            )  # noqa: E501

        self._wals = wals
