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


class SystemInfo(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(
        self,
        barman_ver=None,
        kernel_ver=None,
        python_ver=None,
        release=None,
        rsync_ver=None,
        ssh_ver=None,
        timestamp=None,
    ):  # noqa: E501
        """SystemInfo - a model defined in OpenAPI

        :param barman_ver: The barman_ver of this SystemInfo.  # noqa: E501
        :type barman_ver: str
        :param kernel_ver: The kernel_ver of this SystemInfo.  # noqa: E501
        :type kernel_ver: str
        :param python_ver: The python_ver of this SystemInfo.  # noqa: E501
        :type python_ver: str
        :param release: The release of this SystemInfo.  # noqa: E501
        :type release: str
        :param rsync_ver: The rsync_ver of this SystemInfo.  # noqa: E501
        :type rsync_ver: str
        :param ssh_ver: The ssh_ver of this SystemInfo.  # noqa: E501
        :type ssh_ver: str
        :param timestamp: The timestamp of this SystemInfo.  # noqa: E501
        :type timestamp: str
        """
        self.openapi_types = {
            "barman_ver": str,
            "kernel_ver": str,
            "python_ver": str,
            "release": str,
            "rsync_ver": str,
            "ssh_ver": str,
            "timestamp": str,
        }

        self.attribute_map = {
            "barman_ver": "barman_ver",
            "kernel_ver": "kernel_ver",
            "python_ver": "python_ver",
            "release": "release",
            "rsync_ver": "rsync_ver",
            "ssh_ver": "ssh_ver",
            "timestamp": "timestamp",
        }

        self._barman_ver = barman_ver
        self._kernel_ver = kernel_ver
        self._python_ver = python_ver
        self._release = release
        self._rsync_ver = rsync_ver
        self._ssh_ver = ssh_ver
        self._timestamp = timestamp

    @classmethod
    def from_dict(cls, dikt):
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The SystemInfo of this SystemInfo.  # noqa: E501
        :rtype: SystemInfo
        """
        return util.deserialize_model(dikt, cls)

    @property
    def barman_ver(self):
        """Gets the barman_ver of this SystemInfo.

        Version of Barman which generated the diagnose output  # noqa: E501

        :return: The barman_ver of this SystemInfo.
        :rtype: str
        """
        return self._barman_ver

    @barman_ver.setter
    def barman_ver(self, barman_ver):
        """Sets the barman_ver of this SystemInfo.

        Version of Barman which generated the diagnose output  # noqa: E501

        :param barman_ver: The barman_ver of this SystemInfo.
        :type barman_ver: str
        """
        if barman_ver is None:
            raise ValueError(
                "Invalid value for `barman_ver`, must not be `None`"
            )  # noqa: E501

        self._barman_ver = barman_ver

    @property
    def kernel_ver(self):
        """Gets the kernel_ver of this SystemInfo.

        Information about the OS kernel on which Barman server is running  # noqa: E501

        :return: The kernel_ver of this SystemInfo.
        :rtype: str
        """
        return self._kernel_ver

    @kernel_ver.setter
    def kernel_ver(self, kernel_ver):
        """Sets the kernel_ver of this SystemInfo.

        Information about the OS kernel on which Barman server is running  # noqa: E501

        :param kernel_ver: The kernel_ver of this SystemInfo.
        :type kernel_ver: str
        """
        if kernel_ver is None:
            raise ValueError(
                "Invalid value for `kernel_ver`, must not be `None`"
            )  # noqa: E501

        self._kernel_ver = kernel_ver

    @property
    def python_ver(self):
        """Gets the python_ver of this SystemInfo.

        Version of Python used by Barman server  # noqa: E501

        :return: The python_ver of this SystemInfo.
        :rtype: str
        """
        return self._python_ver

    @python_ver.setter
    def python_ver(self, python_ver):
        """Sets the python_ver of this SystemInfo.

        Version of Python used by Barman server  # noqa: E501

        :param python_ver: The python_ver of this SystemInfo.
        :type python_ver: str
        """
        if python_ver is None:
            raise ValueError(
                "Invalid value for `python_ver`, must not be `None`"
            )  # noqa: E501

        self._python_ver = python_ver

    @property
    def release(self):
        """Gets the release of this SystemInfo.

        Information about the specific OS release on which Barman server is running   # noqa: E501

        :return: The release of this SystemInfo.
        :rtype: str
        """
        return self._release

    @release.setter
    def release(self, release):
        """Sets the release of this SystemInfo.

        Information about the specific OS release on which Barman server is running   # noqa: E501

        :param release: The release of this SystemInfo.
        :type release: str
        """
        if release is None:
            raise ValueError(
                "Invalid value for `release`, must not be `None`"
            )  # noqa: E501

        self._release = release

    @property
    def rsync_ver(self):
        """Gets the rsync_ver of this SystemInfo.

        Version of Rsync used by Barman server  # noqa: E501

        :return: The rsync_ver of this SystemInfo.
        :rtype: str
        """
        return self._rsync_ver

    @rsync_ver.setter
    def rsync_ver(self, rsync_ver):
        """Sets the rsync_ver of this SystemInfo.

        Version of Rsync used by Barman server  # noqa: E501

        :param rsync_ver: The rsync_ver of this SystemInfo.
        :type rsync_ver: str
        """
        if rsync_ver is None:
            raise ValueError(
                "Invalid value for `rsync_ver`, must not be `None`"
            )  # noqa: E501

        self._rsync_ver = rsync_ver

    @property
    def ssh_ver(self):
        """Gets the ssh_ver of this SystemInfo.

        Version of ssh used by Barman server  # noqa: E501

        :return: The ssh_ver of this SystemInfo.
        :rtype: str
        """
        return self._ssh_ver

    @ssh_ver.setter
    def ssh_ver(self, ssh_ver):
        """Sets the ssh_ver of this SystemInfo.

        Version of ssh used by Barman server  # noqa: E501

        :param ssh_ver: The ssh_ver of this SystemInfo.
        :type ssh_ver: str
        """
        if ssh_ver is None:
            raise ValueError(
                "Invalid value for `ssh_ver`, must not be `None`"
            )  # noqa: E501

        self._ssh_ver = ssh_ver

    @property
    def timestamp(self):
        """Gets the timestamp of this SystemInfo.

        The system time of the Barman server (in ISO 8601 format in the local timezone of the server)   # noqa: E501

        :return: The timestamp of this SystemInfo.
        :rtype: str
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this SystemInfo.

        The system time of the Barman server (in ISO 8601 format in the local timezone of the server)   # noqa: E501

        :param timestamp: The timestamp of this SystemInfo.
        :type timestamp: str
        """
        if timestamp is None:
            raise ValueError(
                "Invalid value for `timestamp`, must not be `None`"
            )  # noqa: E501

        self._timestamp = timestamp
