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


class CopyStatsAnalysisTimePerItem(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, pgdata=None, tablespace=None):  # noqa: E501
        """CopyStatsAnalysisTimePerItem - a model defined in OpenAPI

        :param pgdata: The pgdata of this CopyStatsAnalysisTimePerItem.  # noqa: E501
        :type pgdata: float
        :param tablespace: The tablespace of this CopyStatsAnalysisTimePerItem.  # noqa: E501
        :type tablespace: float
        """
        self.openapi_types = {
            'pgdata': float,
            'tablespace': float
        }

        self.attribute_map = {
            'pgdata': 'pgdata',
            'tablespace': 'TABLESPACE'
        }

        self._pgdata = pgdata
        self._tablespace = tablespace

    @classmethod
    def from_dict(cls, dikt):
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CopyStats_analysis_time_per_item of this CopyStatsAnalysisTimePerItem.  # noqa: E501
        :rtype: CopyStatsAnalysisTimePerItem
        """
        return util.deserialize_model(dikt, cls)

    @property
    def pgdata(self):
        """Gets the pgdata of this CopyStatsAnalysisTimePerItem.

        Number of seconds spent in the analysis phase for PGDATA  # noqa: E501

        :return: The pgdata of this CopyStatsAnalysisTimePerItem.
        :rtype: float
        """
        return self._pgdata

    @pgdata.setter
    def pgdata(self, pgdata):
        """Sets the pgdata of this CopyStatsAnalysisTimePerItem.

        Number of seconds spent in the analysis phase for PGDATA  # noqa: E501

        :param pgdata: The pgdata of this CopyStatsAnalysisTimePerItem.
        :type pgdata: float
        """

        self._pgdata = pgdata

    @property
    def tablespace(self):
        """Gets the tablespace of this CopyStatsAnalysisTimePerItem.

        Number of seconds spent in the analysis phase for TABLESPACE  # noqa: E501

        :return: The tablespace of this CopyStatsAnalysisTimePerItem.
        :rtype: float
        """
        return self._tablespace

    @tablespace.setter
    def tablespace(self, tablespace):
        """Sets the tablespace of this CopyStatsAnalysisTimePerItem.

        Number of seconds spent in the analysis phase for TABLESPACE  # noqa: E501

        :param tablespace: The tablespace of this CopyStatsAnalysisTimePerItem.
        :type tablespace: float
        """

        self._tablespace = tablespace