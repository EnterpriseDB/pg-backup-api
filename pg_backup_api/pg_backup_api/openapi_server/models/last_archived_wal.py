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

# This file was autogenerated by OpenAPI Generator.

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from pg_backup_api.openapi_server.models.base_model_ import Model
from pg_backup_api.openapi_server import util


class LastArchivedWal(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, compression=None, name=None, size=None, time=None):  # noqa: E501
        """LastArchivedWal - a model defined in OpenAPI

        :param compression: The compression of this LastArchivedWal.  # noqa: E501
        :type compression: str
        :param name: The name of this LastArchivedWal.  # noqa: E501
        :type name: str
        :param size: The size of this LastArchivedWal.  # noqa: E501
        :type size: int
        :param time: The time of this LastArchivedWal.  # noqa: E501
        :type time: float
        """
        self.openapi_types = {
            'compression': str,
            'name': str,
            'size': int,
            'time': float
        }

        self.attribute_map = {
            'compression': 'compression',
            'name': 'name',
            'size': 'size',
            'time': 'time'
        }

        self._compression = compression
        self._name = name
        self._size = size
        self._time = time

    @classmethod
    def from_dict(cls, dikt):
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The LastArchivedWal of this LastArchivedWal.  # noqa: E501
        :rtype: LastArchivedWal
        """
        return util.deserialize_model(dikt, cls)

    @property
    def compression(self):
        """Gets the compression of this LastArchivedWal.

        Compression algorithm used to compress the WAL  # noqa: E501

        :return: The compression of this LastArchivedWal.
        :rtype: str
        """
        return self._compression

    @compression.setter
    def compression(self, compression):
        """Sets the compression of this LastArchivedWal.

        Compression algorithm used to compress the WAL  # noqa: E501

        :param compression: The compression of this LastArchivedWal.
        :type compression: str
        """

        self._compression = compression

    @property
    def name(self):
        """Gets the name of this LastArchivedWal.

        Name of the WAL segment  # noqa: E501

        :return: The name of this LastArchivedWal.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this LastArchivedWal.

        Name of the WAL segment  # noqa: E501

        :param name: The name of this LastArchivedWal.
        :type name: str
        """

        self._name = name

    @property
    def size(self):
        """Gets the size of this LastArchivedWal.

        Size in bytes of the WAL stored on the Barman server  # noqa: E501

        :return: The size of this LastArchivedWal.
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size):
        """Sets the size of this LastArchivedWal.

        Size in bytes of the WAL stored on the Barman server  # noqa: E501

        :param size: The size of this LastArchivedWal.
        :type size: int
        """

        self._size = size

    @property
    def time(self):
        """Gets the time of this LastArchivedWal.

        Timestamp in epoch time format representing the time this WAL was archived by Barman   # noqa: E501

        :return: The time of this LastArchivedWal.
        :rtype: float
        """
        return self._time

    @time.setter
    def time(self, time):
        """Sets the time of this LastArchivedWal.

        Timestamp in epoch time format representing the time this WAL was archived by Barman   # noqa: E501

        :param time: The time of this LastArchivedWal.
        :type time: float
        """

        self._time = time