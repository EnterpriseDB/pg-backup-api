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
from pg_backup_api.openapi_server import util


class CopyStatsSerializedCopyTimePerItem(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, pgdata=None, tablespace=None, filename=None):  # noqa: E501
        """CopyStatsSerializedCopyTimePerItem - a model defined in OpenAPI

        :param pgdata: The pgdata of this CopyStatsSerializedCopyTimePerItem.  # noqa: E501
        :type pgdata: float
        :param tablespace: The tablespace of this CopyStatsSerializedCopyTimePerItem.  # noqa: E501
        :type tablespace: float
        :param filename: The filename of this CopyStatsSerializedCopyTimePerItem.  # noqa: E501
        :type filename: float
        """
        self.openapi_types = {"pgdata": float, "tablespace": float, "filename": float}

        self.attribute_map = {
            "pgdata": "pgdata",
            "tablespace": "TABLESPACE",
            "filename": "FILENAME",
        }

        self._pgdata = pgdata
        self._tablespace = tablespace
        self._filename = filename

    @classmethod
    def from_dict(cls, dikt):
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CopyStats_serialized_copy_time_per_item of this CopyStatsSerializedCopyTimePerItem.  # noqa: E501
        :rtype: CopyStatsSerializedCopyTimePerItem
        """
        return util.deserialize_model(dikt, cls)

    @property
    def pgdata(self):
        """Gets the pgdata of this CopyStatsSerializedCopyTimePerItem.

        Total number of seconds spent by all copy jobs copying the data for PGDATA   # noqa: E501

        :return: The pgdata of this CopyStatsSerializedCopyTimePerItem.
        :rtype: float
        """
        return self._pgdata

    @pgdata.setter
    def pgdata(self, pgdata):
        """Sets the pgdata of this CopyStatsSerializedCopyTimePerItem.

        Total number of seconds spent by all copy jobs copying the data for PGDATA   # noqa: E501

        :param pgdata: The pgdata of this CopyStatsSerializedCopyTimePerItem.
        :type pgdata: float
        """

        self._pgdata = pgdata

    @property
    def tablespace(self):
        """Gets the tablespace of this CopyStatsSerializedCopyTimePerItem.

        Total number of seconds spent by all copy jobs copying the data for TABLESPACE   # noqa: E501

        :return: The tablespace of this CopyStatsSerializedCopyTimePerItem.
        :rtype: float
        """
        return self._tablespace

    @tablespace.setter
    def tablespace(self, tablespace):
        """Sets the tablespace of this CopyStatsSerializedCopyTimePerItem.

        Total number of seconds spent by all copy jobs copying the data for TABLESPACE   # noqa: E501

        :param tablespace: The tablespace of this CopyStatsSerializedCopyTimePerItem.
        :type tablespace: float
        """

        self._tablespace = tablespace

    @property
    def filename(self):
        """Gets the filename of this CopyStatsSerializedCopyTimePerItem.

        Total number of seconds spent by all copy jobs copying the data for FILENAME   # noqa: E501

        :return: The filename of this CopyStatsSerializedCopyTimePerItem.
        :rtype: float
        """
        return self._filename

    @filename.setter
    def filename(self, filename):
        """Sets the filename of this CopyStatsSerializedCopyTimePerItem.

        Total number of seconds spent by all copy jobs copying the data for FILENAME   # noqa: E501

        :param filename: The filename of this CopyStatsSerializedCopyTimePerItem.
        :type filename: float
        """

        self._filename = filename
