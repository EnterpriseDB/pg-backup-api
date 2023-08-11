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
Logic for performing recovery operations through the pg-backup-api.

:var DEFAULT_OP_TYPE: default operation to be performed, if none is specified.
:var JOBS_DIR: name of the directory where to save files that indicate a
    recovery operation has been created.
:var OUTPUT_DIR: name of the directory where to save files that contain the
    output of a finished recovery operation -- both for failed and successfull
    executions.
:var REQUIRED_OPTIONS: tuple of required options for performing an operation
    through the pg-backup-api.
"""
import argparse
import json
import logging
import os
import sys
from typing import Any, Callable, Dict, List, Optional

from datetime import datetime
from os.path import join

from pg_backup_api.utils import barman, load_barman_config, get_server_by_name

load_barman_config()

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger()


DEFAULT_OP_TYPE = "recovery"
JOBS_DIR = "jobs"
OUTPUT_DIR = "output"
REQUIRED_OPTIONS = ("backup_id", "destination_directory", "remote_ssh_command")


class Metadata:
    """
    Contain metadata about a Barman server, and possibly about an operation.

    :ivar operation_type: type of the operation, by default ``recovery``.
    :ivar operation_id: ID of the recovery operation, if any.
    :ivar server_name: name of the Barman server.
    :ivar server_config: Barman configuration of the Barman server.
    :ivar jobs_basedir: directory where to save files of recovery operations
        that have been created for this Barman server.
    :ivar output_basedir: directory where to save files with output of recovery
        operations that have been finished for this Barman server -- both for
        failed and successful executions.
    """
    def __init__(self, server_name: str,
                 operation_id: Optional[str] = None) -> None:
        """
        Initialize a new instance of :class:`Metadata`.

        Fill all the metadata required by pg-backup-api of a given Barman
        server named *server_name*, if it exists in Barman.

        :param server_name: name of the Barman server.
        :param operation_id: ID of the recovery operation, if any.

        :raises:
            :exc:`ServerOperationConfigError`: if no Barman configuration could
                be found for server *server_name*.
        """
        self.operation_type = DEFAULT_OP_TYPE
        self.operation_id = operation_id
        self.server_name = server_name
        self.server_config = get_server_by_name(server_name)
        if not self.server_config:
            raise ServerOperationConfigError(
                f"No barman config found for '{server_name}'."
            )

        barman_home = barman.__config__.barman_home
        self.jobs_basedir = join(barman_home, server_name, JOBS_DIR)
        self.output_basedir = join(barman_home, server_name, OUTPUT_DIR)


class ServerOperation(Metadata):
    """Represent a pg-backup-api recovery operation."""

    def get_operations_list(self) -> List[str]:
        """
        Get the list of recovery operations of this Barman server.

        Fetch operation IDs from all ``.json`` files found under the
        :attr:`jobs_basedir` of this server.

        :return: list of IDs of all recovery operations of this Barman server.
        """
        jobs_list = []
        jobs_basedir = self.jobs_basedir
        if os.path.exists(jobs_basedir):
            for job in [files for _, _, files in os.walk(jobs_basedir)][0]:
                if job.endswith(".json"):
                    operation_id, _ = job.split(".json")
                    jobs_list.append(operation_id)
        return jobs_list

    def get_status_by_operation_id(self) -> str:
        """
        Get the status of a specific recovery operation.

        .. note::
            :attr:`operation_id` must have been filled before calling this
            method.

        :return: the status of the recovery operation, which may be one among:
            ``IN_PROGRESS``, ``DONE``, or ``FAILED``.

        :raises:
            :exc:`Exception` if :attr:`operation_id` is invalid.
        """
        output_file = self.get_output_file()
        if not os.path.exists(output_file):
            if os.path.exists(self.get_job_file()):
                return "IN_PROGRESS"
            else:
                raise Exception("Invalid operation-id")

        with open(self.get_output_file()) as file_object:
            content = json.load(file_object)
            return "DONE" if content.get("success") else "FAILED"

    @staticmethod
    def time_event_now() -> str:
        """
        Get current timestamp.

        :return: current timestamp in the format ``%Y-%m-%dT%H:%M:%S.%f``.
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

    def copy_and_validate_options(self, general_options: Dict[str, str]) \
            -> Dict[str, str]:
        """
        Get information about the recovery operation to be saved in a job file.

        .. note::
            A :exc:`KeyError` will be implicitly raised if *generation_options*
            does not contain a key specified in :data:`REQUIRED_OPTIONS`.

        :param general_options: a Python :class:`dict` containing the values
            for the keys of :data:`REQUIRED_OPTIONS`.
        :return: a Python :class:`dict` instance with the following keys:

            * ``operation_type``: type of the operation, e.g. ``recovery``;
            * ``start_time``: current timestamp in the format
              ``%Y-%m-%dT%H:%M:%S.%f``;
            * keys specified through :data:`REQUIRED_OPTIONS`.
        """
        job_data = {
            "operation_type": self.operation_type,
            "start_time": ServerOperation.time_event_now(),
        }
        for required_key in REQUIRED_OPTIONS:
            job_data[required_key] = general_options[required_key]

        return job_data

    def create_job_file(self, general_options: Dict[str, str]) -> None:
        """
        Create a job file to represent a requested recovery operation.

        File is created under :attr:`jobs_basedir`. Its content is gotten
        through :meth:`copy_and_validate_options`.

        .. note::
            If the directories pointed by :attr:`jobs_basedir` and
            :attr:`output_basedir` do not exist yet, this method will take care
            of creating them.

        :param general_options: a Python :class:`dict` containing the values
            for the keys of :data:`REQUIRED_OPTIONS`.
        """
        if not os.path.exists(self.jobs_basedir):
            os.makedirs(self.jobs_basedir)

        job_data = self.copy_and_validate_options(general_options)
        self.__create_file(self.jobs_basedir, job_data)

    def create_output_file(self, content_file: Dict[str, str]) -> None:
        """
        Create an output file to represent the output of a recovery operation.

        :param content_file: the content to be written in the created file.
            Expects a Python dictionary which will be converted to JSON.
        """
        if not os.path.exists(self.output_basedir):
            os.makedirs(self.output_basedir)

        self.__create_file(self.output_basedir, content_file)

    def __create_file(self, file_type: str, content: Dict[str, str]) -> None:
        """
        Create a file under *file_type* directory with *content*.

        The file will be named ":attr:`operation_id`.json".

        :param file_type: directory under which the file should be created.
        :param content: content to be written into the file. Expects a Python
            dictionary which will be converted to JSON.

        :raises:
            :exc:`Exception` if :attr:`operation_id` has not been filled before
                calling this method, or if the file already exists.
        """
        if not self.operation_id:
            raise Exception("operation_id is required here")

        file_name = f"{self.operation_id}.json"
        fpath = join(file_type, file_name)
        if os.path.exists(fpath):
            raise Exception("duplicated operation-id")

        with open(fpath, "w") as written_file:
            json.dump(content, written_file)

    def get_job_file_content(self) -> Dict[str, str]:
        """
        Get the content of the recovery operation job file.

        :return: a Python :class:`dict` object representing the JSON content
            of the job file of the recovery operation.
        """
        with open(self.get_job_file()) as file_object:
            return json.load(file_object)

    def get_output_file(self) -> str:
        """
        Get the path to the output file related to the recovery operation.

        :return: path to the output file.
        """
        return self.__files_path(self.output_basedir)

    def get_job_file(self) -> str:
        """
        Get the path to the job file related to the recovery operation.

        :return: path to the job file.
        """
        return self.__files_path(self.jobs_basedir)

    def __files_path(self, basedir: str) -> str:
        """
        Get the path to a file named ":attr:`operation_id`.json".

        The file is considered to be under *basedir*.

        :param basedir: the path of the directory under which the file should
            be.
        :return: *basedir* joined in ``os.path`` fashion with the file name
            (":attr:`operation_id`.json")

        :raises:
            :exc:`Exception`: if *basedir* does not exist, or if
                :attr:`operation_id` has not been filled before calling this
                method.
        """
        if not os.path.exists(basedir):
            msg = f"Couldn't find a task for server '{self.server_name}'"
            raise Exception(msg)

        if not self.operation_id:
            raise Exception("operation_id is required here")

        file_name = f"{self.operation_id}.json"
        fpath = join(basedir, file_name)
        return fpath


class ServerOperationConfigError(ValueError):
    """Indicate Barman does not have configuration for the given server."""
    pass


def main(callback: Callable[..., Any]) -> int:
    """
    Execute *callback* and log its output as an ``INFO`` message.

    .. note::
        If any issue is faced, log the exception as an ``ERROR`` message
        instead of logging the command output as an ``INFO`` message.

    :param callback: reference to any method from a :class:`ServerOperation`
        object.
    :return: ``-1`` if any issue is faced while executing *callback*, otherwise
        ``0``.
    """
    try:
        log.info(callback())
    except Exception as e:
        # TODO: we might behave differently depending upon the type here
        log.error(e)
        return -1

    return 0


if __name__ == "__main__":
    # If this module is run as the entry point, expose a command-line argument
    # parser. It exposes the same operations that are exposed through the REST
    # API, i.e., list, create and get recovery operations.
    operations_commands = {
        "list-operations": "get_operations_list",
        "create-operation": "create_job_file",
        "get-operation": "get_status_by_operation_id",
    }
    parser = argparse.ArgumentParser(
        description="Alternative to the REST API, so one can list, create and "
                    "get information about jobs without a running REST API.",
    )
    parser.add_argument(
        "--server-name", required=True,
        help="Name of the Barman server related to the recovery "
             "operation.",
    )
    parser.add_argument(
        "--operation-id",
        help="ID of the recovery operation, if you are trying to query an "
             "existing operation."
    )
    parser.add_argument(
        "command",
        choices=operations_commands.keys(),
        help="What we should do -- list recovery operations, create a new "
             "recovery operation, or get info about a specific recovery "
             "operation.",
    )

    args = parser.parse_args()
    op = ServerOperation(args.server_name, args.operation_id)
    callback = getattr(op, operations_commands[args.command])

    retval = main(callback)
    sys.exit(retval)
