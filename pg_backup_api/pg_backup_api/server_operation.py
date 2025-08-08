# -*- coding: utf-8 -*-
# © Copyright EnterpriseDB UK Limited 2021-2025 - All rights reserved.
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
Logic for performing operations through the pg-backup-api.

:data DEFAULT_OP_TYPE: default operation to be performed (``recovery``), if
none is specified.
"""
from abc import abstractmethod
import argparse
from enum import Enum
import json
import logging
import os
import subprocess
import sys
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    TYPE_CHECKING,
)

from datetime import datetime
from os.path import join

from pg_backup_api.utils import barman, load_barman_config, get_server_by_name

if TYPE_CHECKING:  # pragma: no cover
    from barman.config import Config as BarmanConfig

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger()


class OperationType(Enum):
    """Describe operations that can be performed through pg-backup-api."""

    RECOVERY = "recovery"
    CONFIG_SWITCH = "config_switch"
    CONFIG_UPDATE = "config_update"


DEFAULT_OP_TYPE = OperationType.RECOVERY


class OperationServerConfigError(ValueError):
    """Indicate Barman does not have configuration for the given server."""

    pass


class MalformedContent(ValueError):
    """When trying to write corrupted content to a file."""

    pass


class OperationNotExists(LookupError):
    """If trying to fetch information about a non-existing operation."""

    pass


class OperationServer:
    """
    Contain logic to handle operations for a Barman instance or Barman server.

    :ivar name: name of the Barman server, if it's server operation, otherwise
        ``None`` for a "global" (instance) operation.
    :ivar config: Barman configuration of the Barman server, if it's a server
        operation, otherwise ``None`` for a "global" (instance) operation.
    :ivar jobs_basedir: directory where to save files of operations that have
        been created for this Barman server or instance.
    :ivar output_basedir: directory where to save files with output of
        operations that have been finished for this Barman server or instance
        -- both for failed and successful executions.
    """

    # Name of the pg-backup-api ``jobs`` directory. Files created under this
    # directory indicate the corresponding operation has been created.
    _JOBS_DIR_NAME = "jobs"
    # Name of the pg-backup-api ``output`` directory. Files created under this
    # directory indicate the corresponding operation has finished running --
    # either it has failed or has succeeded.
    _OUTPUT_DIR_NAME = "output"
    # Set of required keys when creating an operation job file.
    _REQUIRED_JOB_KEYS = (
        "operation_type",
        "start_time",
    )
    # Set of required keys when creating an operation output file.
    _REQUIRED_OUTPUT_KEYS = (
        "success",
        "end_time",
        "output",
    )

    def __init__(self, name: Optional[str]) -> None:
        """
        Initialize a new instance of :class:`OperationServer`.

        Fill all the metadata required by pg-backup-api for a given Barman
        server named *name*, if a Barman server opartion and the server exists
        in Barman. Also prepare the Barman server or instance to execute
        pg-backup-api operations.

        :param name: name of the Barman server, if it's a Barman server
            operation, ``None`` for a "global" (instance) operation.

        :raises:
            :exc:`OperationServerConfigError`: if no Barman configuration could
                be found for server *name*, in case of a Barman server
                operation.
        """
        self.name = name
        self.config = None

        load_barman_config()

        if name:
            self.config = get_server_by_name(name)

            if not self.config:
                raise OperationServerConfigError(
                    f"No barman config found for '{name}'."
                )

        if TYPE_CHECKING:  # pragma: no cover
            assert isinstance(barman.__config__, BarmanConfig)

        #TODO: barman_home can be undefined in the config
        barman_home = barman.__config__.barman_home

        if name:
            self.jobs_basedir = join(barman_home, name, self._JOBS_DIR_NAME)
            self.output_basedir = join(
                barman_home, name, self._OUTPUT_DIR_NAME
            )
        else:
            self.jobs_basedir = join(barman_home, self._JOBS_DIR_NAME)
            self.output_basedir = join(barman_home, self._OUTPUT_DIR_NAME)

        self._create_jobs_dir()
        self._create_output_dir()

    @staticmethod
    def _create_dir(dir_path: str) -> None:
        """
        Create a directory pointed by *dir_path*.

        .. note::
            Do nothing if the directory already exists.

        :param dir_path: path where the directory will be created.

        :raises:
            :exc:`NotADirectoryError`: if path pointed by *dir_path* already
                exists, but it is not a directory.
        """
        if os.path.exists(dir_path):
            if not os.path.isdir(dir_path):
                msg = f"'{dir_path}' exists but it is not a directory"
                raise NotADirectoryError(msg)
        else:
            os.makedirs(dir_path)

    def _create_jobs_dir(self) -> None:
        """Create the ``jobs`` directory of Barman server or instance."""
        self._create_dir(self.jobs_basedir)

    def _create_output_dir(self) -> None:
        """Create the ``outputs`` directory of Barman server or instance."""
        self._create_dir(self.output_basedir)

    def get_job_file_path(self, op_id: str) -> str:
        """
        Get path to the job file of operation *op_id*.

        :param op_id: ID of the pg-backup-api operation.
        :return: path to job file of operation *op_id*.
        """
        return os.path.join(self.jobs_basedir, f"{op_id}.json")

    def get_output_file_path(self, op_id: str) -> str:
        """
        Get path to the output file of operation *op_id*.

        :param op_id: ID of the pg-backup-api operation.
        :return: path to output file of operation *op_id*.
        """
        return os.path.join(self.output_basedir, f"{op_id}.json")

    @staticmethod
    def _write_file(file_path: str, content: Dict[str, Any]) -> None:
        """
        Write a file to *file_path* with *content*.

        :param file_path: path where to write the file.
        :param content: content to be written to the file. Expected to be
            parsable as JSON.

        :raises:
            :exc:`FileExistsError` if *file_path* already exists. Raised both
                if *file_path* is already a file or a directory.
        """
        if os.path.exists(file_path):
            raise FileExistsError(f"File '{file_path}' already exists")

        with open(file_path, "w") as fd:
            json.dump(content, fd)

    def write_job_file(self, op_id: str, content: Dict[str, Any]) -> None:
        """
        Create a job file to represent a requested operation.

        File is created under :attr:`jobs_basedir`.

        .. note::
            Creating a job file means you are registering the operation.

        :param content: content to be written into the created job file.
            Expects a Python dictionary which will be converted to JSON. It
            should contain at least the keys :attr:`_REQUIRED_JOB_KEYS`.

        :raises:
            :exc:`MalformedContent`: if *content* is missing required keys.
            :exc:`FileExistsError`: if the path to the file to be written
                already exists.
        """
        required_keys: Set[str] = set(self._REQUIRED_JOB_KEYS)
        missing_keys = required_keys - set(content.keys())

        if missing_keys:
            msg = (
                f"Job file for operation '{op_id}' is missing required "
                f"keys: {', '.join(sorted(missing_keys))}"
            )
            raise MalformedContent(msg)

        try:
            self._write_file(self.get_job_file_path(op_id), content)
        except FileExistsError:
            msg = f"Job file for operation '{op_id}' already exists"
            raise FileExistsError(msg)

    def write_output_file(self, op_id: str, content: Dict[str, Any]) -> None:
        """
        Create an output file to represent the output of an operation.

        File is created under :attr:`output_basedir`.

        .. note::
            Creating an output file means you are finishing the execution of
            the operation.

        :param content: content to be written into the created output file.
            Expects a Python dictionary which will be converted to JSON. It
            should contain at least the keys :attr:`_REQUIRED_OUTPUT_KEYS`.

        :raises:
            :exc:`MalformedContent`: if *content* is missing required keys.
            :exc:`FileExistsError`: if the path to the file to be written
                already exists.
        """
        required_keys: Set[str] = set(self._REQUIRED_OUTPUT_KEYS)
        missing_keys = required_keys - set(content.keys())

        if missing_keys:
            msg = (
                f"Output file for operation '{op_id}' is missing required "
                f"keys: {', '.join(sorted(missing_keys))}"
            )
            raise MalformedContent(msg)

        try:
            self._write_file(self.get_output_file_path(op_id), content)
        except FileExistsError:
            msg = f"Output file for operation '{op_id}' already exists"
            raise FileExistsError(msg)

    @staticmethod
    def _read_file(file_path: str) -> Dict[str, Any]:
        """
        Read file pointed by *file_path*.

        File should contain JSON parsable content.

        :param file_path: path to the file to be read and parsed.

        :return: a Python dictionary with the contents of file *file_path*.
        """
        with open(file_path) as fd:
            return json.load(fd)

    def read_job_file(self, op_id: str) -> Dict[str, Any]:
        """
        Read the job file of operation *op_id*.

        :param op_id: ID of the operation which job file should be read.
        :return: a Python dictionary representing the JSON content of the job
            file.

        :raises:
            :exc:`FileNotFoundError`: if the job file for operation *op_id*
                could not be found.
        """
        try:
            return self._read_file(self.get_job_file_path(op_id))
        except FileNotFoundError:
            msg = f"Job file for operation '{op_id}' does not exist"
            raise FileNotFoundError(msg)

    def read_output_file(self, op_id: str) -> Dict[str, Any]:
        """
        Read the output file of operation *op_id*.

        :param op_id: ID of the operation which output file should be read.
        :return: a Python dictionary representing the JSON content of the
            output file.

        :raises:
            :exc:`FileNotFoundError`: if the output file for operation *op_id*
                could not be found.
        """
        try:
            return self._read_file(self.get_output_file_path(op_id))
        except FileNotFoundError:
            msg = f"Output file for operation '{op_id}' does not exist"
            raise FileNotFoundError(msg)

    def get_operations_list(
        self, op_type: Optional[OperationType] = None
    ) -> List[Dict[str, Any]]:
        """
        Get the list of operations of this Barman server or instance.

        Fetch operation from all ``.json`` files found under the
        :attr:`jobs_basedir` of this server or instance.

        :param op_type: if ``None`` retrieve all operations. If something other
            than ``None``, filter by the given type.

        :return: list of operations of this Barman server or instance. Each
            item has the following keys:

            * ``id``: ID of the operation;
            * ``type``: type of the operation.
        """
        op_type_aux: Optional[str] = op_type.value if op_type else None
        jobs_list = []

        for job_file in os.listdir(self.jobs_basedir):
            if not job_file.endswith(".json"):
                continue

            op_id, _ = job_file.split(".json")

            content = self.read_job_file(op_id)
            operation_type = content.get("operation_type")

            if operation_type == (op_type_aux or operation_type):
                jobs_list.append(
                    {
                        "id": op_id,
                        "type": operation_type,
                    }
                )

        return jobs_list

    def get_operation_status(self, op_id: str) -> str:
        """
        Get the status of the operation *op_id*.

        :param op_id: ID of the operation which status should be retrieved.
        :return: status of the operation. Can be one among: ``DONE``,
            ``FAILED``, or ``IN_PROGRESS``.

        :raises:
            :exc:`OperationNotExists`: if trying to query the status of a
                non-existing operation.
        """
        try:
            content = self.read_output_file(op_id)
            return "DONE" if content.get("success") else "FAILED"
        except FileNotFoundError:
            pass

        try:
            _ = self.read_job_file(op_id)
            return "IN_PROGRESS"
        except FileNotFoundError:
            raise OperationNotExists(f"Operation '{op_id}' does not exist")


class Operation:
    """
    Contain information about an operation of the pg-backup-api.

    Can be used to create a new operation, or to fetch operation from an
    existing operation.

    This is a superclass. You are expected to inherit from this class to create
    a new operation in the pg-backup-api, and to define at least
    :meth:`_run_logic` when doing that.

    :ivar server: an instance of :class:`OperationServer`. Used for helping
        with management of this operation.
    :ivar id: ID of this operation.
    """

    def __init__(
        self, server_name: Optional[str], id: Optional[str] = None
    ) -> None:
        """
        Initialize a new instance of :class:`Operation`.

        :param server_name: name of the Barman server, in case of a Barman
            server operation, ``None`` in case of a Barman instance operation.
        :param id: ID of the operation. Useful when querying an existing
            operation. Use ``None`` when creating an operation, so this class
            generates a new ID.
        """
        self.server = OperationServer(server_name)
        self.id = id or self._generate_id()

    @staticmethod
    def _generate_id() -> str:
        """
        Generate an ID for a new operation.

        :return: current timestamp in the format ``%Y%m%dT%H%M%S``.
        """
        return datetime.now().strftime("%Y%m%dT%H%M%S")

    @staticmethod
    def time_event_now() -> str:
        """
        Get current timestamp.

        :return: current timestamp in the format ``%Y-%m-%dT%H:%M:%S.%f``.
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

    @property
    def job_file(self) -> str:
        """Path to the job file of this operation."""
        return self.server.get_job_file_path(self.id)

    @property
    def output_file(self) -> str:
        """Path to the output file of this operation."""
        return self.server.get_output_file_path(self.id)

    def read_job_file(self) -> Dict[str, Any]:
        """
        Read the job file of this operation.

        .. note::
            See :meth:`OperationServer.read_job_file` for more details.

        :return: a Python dictionary representing the JSON content of the job
            file.
        """
        return self.server.read_job_file(self.id)

    def read_output_file(self) -> Dict[str, Any]:
        """
        Read the output file of this operation.

        .. note::
            See :meth:`OperationServer.read_output_file` for more details.

        :return: a Python dictionary representing the JSON content of the
            output file.
        """
        return self.server.read_output_file(self.id)

    def write_job_file(self, content: Dict[str, Any]) -> None:
        """
        Write the job file of this operation.

        .. note::
            See :meth:`OperationServer.write_job_file` for more details.

        :param content: a Python dictionary representing the JSON content of
            the job file.
        """
        self.server.write_job_file(self.id, content)

    def write_output_file(self, content: Dict[str, Any]) -> None:
        """
        Write the output file of this operation.

        .. note::
            See :meth:`OperationServer.write_output_file` for more details.

        :param content: a Python dictionary representing the JSON content of
            the output file.
        """
        self.server.write_output_file(self.id, content)

    def get_status(self) -> str:
        """
        Get the status of this operation.

        .. note::
            See :meth:`OperationServer.get_operation_status` for more details.

        :return: status of this operation. Can be one among: ``DONE``,
            ``FAILED``, or ``IN_PROGRESS``.
        """
        return self.server.get_operation_status(self.id)

    @staticmethod
    def _run_subprocess(
        cmd: List[str],
    ) -> Tuple[Union[str, bytearray, memoryview], Union[int, Any]]:
        """
        Run *cmd* as a subprocess.

        :param cmd: list of strings composing the command to be ran.

        :return: a tuple consisting of:

            * ``stdout``/``stderr`` of the command;
            * exit code of the command.
        """
        process = subprocess.Popen(
            cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE
        )
        stdout, _ = process.communicate()
        stdout = stdout.decode() if isinstance(stdout, bytes) else stdout
        return stdout, process.returncode

    @abstractmethod
    def _run_logic(
        self,
    ) -> Tuple[Union[str, bytearray, memoryview], Union[int, Any]]:
        """
        Logic to be ran when executing the operation.

        This method should be defined in the subclass, and will be called when
        running :meth:`run`.

        :return: a tuple consisting of:

            * output of the operation;
            * return code of the operation.
        """
        pass

    def run(self) -> Tuple[Union[str, bytearray, memoryview], Union[int, Any]]:
        """
        Run the operation.

        .. note::
            Make sure to not call this method twice or more for the same
            operation.

        :return: a tuple consisting of:

            * output of the operation;
            * return code of the operation.
        """
        return self._run_logic()


class RecoveryOperation(Operation):
    """
    Contain information and logic to process a recovery operation.

    :cvar REQUIRED_ARGUMENTS: required arguments when creating a recovery
        operation.
    :cvar TYPE: enum type of this operation.
    """

    REQUIRED_ARGUMENTS = (
        "backup_id",
        "destination_directory",
        "remote_ssh_command",
    )
    TYPE = OperationType.RECOVERY

    @classmethod
    def _validate_job_content(cls, content: Dict[str, Any]) -> None:
        """
        Validate the content of the job file before creating it.

        :param content: Python dictionary representing the JSON content of the
            job file.

        :raises:
            :exc:`MalformedContent`: if the set of options in *content* is
                either missing required keys.
        """
        required_args: Set[str] = set(cls.REQUIRED_ARGUMENTS)
        missing_args = required_args - set(content.keys())

        if missing_args:
            msg = (
                "Missing required arguments: "
                f"{', '.join(sorted(missing_args))}"
            )
            raise MalformedContent(msg)

    def write_job_file(self, content: Dict[str, Any]) -> None:
        """
        Write the job file with *content*.

        .. note::
            See :meth:`Operation.write_job_file` for more details.

        :param content: Python dictionary representing the JSON content of the
            job file. Besides what is contained in *content*, this method adds
            the following keys:

            * ``operation_type``: ``recovery``;
            * ``start_time``: current timestamp.
        """
        content["operation_type"] = self.TYPE.value
        content["start_time"] = self.time_event_now()
        self._validate_job_content(content)
        super().write_job_file(content)

    def _get_args(self) -> List[str]:
        """
        Get arguments for running ``barman recover`` command.

        :return: list of arguments for ``barman recover`` command.
        """
        job_content = self.read_job_file()

        backup_id = job_content.get("backup_id")
        destination_directory = job_content.get("destination_directory")
        remote_ssh_command = job_content.get("remote_ssh_command")

        if TYPE_CHECKING:  # pragma: no cover
            assert isinstance(self.server.name, str)
            assert isinstance(backup_id, str)
            assert isinstance(destination_directory, str)
            assert isinstance(remote_ssh_command, str)

        return [
            self.server.name,
            backup_id,
            destination_directory,
            "--remote-ssh-command",
            remote_ssh_command,
        ]

    def _run_logic(
        self,
    ) -> Tuple[Union[str, bytearray, memoryview], Union[int, Any]]:
        """
        Logic to be ran when executing the recovery operation.

        Run ``barman recover`` command with the configured arguments.

        Will be called when running :meth:`Operation.run`.

        :return: a tuple consisting of:

            * ``stdout``/``stderr`` of ``barman recover``;
            * exit code of ``barman recover``.
        """
        cmd = ["barman", "recover"] + self._get_args()
        return self._run_subprocess(cmd)


class ConfigSwitchOperation(Operation):
    """
    Contain information and logic to process a config switch operation.

    :cvar POSSIBLE_ARGUMENTS: possible arguments when creating a config switch
        operation.
    :cvar TYPE: enum type of this operation.
    """

    POSSIBLE_ARGUMENTS = (
        "model_name",
        "reset",
    )
    TYPE = OperationType.CONFIG_SWITCH

    @classmethod
    def _validate_job_content(cls, content: Dict[str, Any]) -> None:
        """
        Validate the content of the job file before creating it.

        :param content: Python dictionary representing the JSON content of the
            job file.

        :raises:
            :exc:`MalformedContent`: if the set of options in *content* is not
                compliant with the supported options and how to use them.
        """
        # One of :attr:`POSSIBLE_ARGUMENTS` must be specified, but not both
        if not any(arg in content for arg in cls.POSSIBLE_ARGUMENTS):
            msg = (
                "One among the following arguments must be specified: "
                f"{', '.join(sorted(cls.POSSIBLE_ARGUMENTS))}"
            )
            raise MalformedContent(msg)
        elif all(arg in content for arg in cls.POSSIBLE_ARGUMENTS):
            msg = (
                "Only one among the following arguments should be specified: "
                f"{', '.join(sorted(cls.POSSIBLE_ARGUMENTS))}"
            )
            raise MalformedContent(msg)

        for key, type_ in [
            (
                "model_name",
                str,
            ),
            (
                "reset",
                bool,
            ),
        ]:
            if key in content and not isinstance(content[key], type_):
                msg = (
                    f"`{key}` is expected to be a `{type_}`, but a "
                    f"`{type(content[key])}` was found instead: "
                    f"`{content[key]}`."
                )
                raise MalformedContent(msg)

        if "reset" in content and content["reset"] is False:
            msg = "Value of `reset` key, if present, can only be `True`"
            raise MalformedContent(msg)

    def write_job_file(self, content: Dict[str, Any]) -> None:
        """
        Write the job file with *content*.

        .. note::
            See :meth:`Operation.write_job_file` for more details.

        :param content: Python dictionary representing the JSON content of the
            job file. Besides what is contained in *content*, this method adds
            the following keys:

            * ``operation_type``: ``config_switch``;
            * ``start_time``: current timestamp.
        """
        content["operation_type"] = self.TYPE.value
        content["start_time"] = self.time_event_now()
        self._validate_job_content(content)
        super().write_job_file(content)

    def _get_args(self) -> List[str]:
        """
        Get arguments for running ``barman config-switch`` command.

        :return: list of arguments for ``barman config-switch`` command.
        """
        job_content = self.read_job_file()

        model_name = job_content.get("model_name")
        reset = job_content.get("reset")

        if TYPE_CHECKING:  # pragma: no cover
            assert isinstance(self.server.name, str)
            assert model_name is None or isinstance(model_name, str)
            assert reset is None or isinstance(reset, bool)

        ret = [self.server.name]

        if model_name:
            ret.append(model_name)
        elif reset:
            ret.append("--reset")

        return ret

    def _run_logic(
        self,
    ) -> Tuple[Union[str, bytearray, memoryview], Union[int, Any]]:
        """
        Logic to be ran when executing the config switch operation.

        Run ``barman config-switch`` command with the configured arguments.

        Will be called when running :meth:`Operation.run`.

        :return: a tuple consisting of:

            * ``stdout``/``stderr`` of ``barman config-switch``;
            * exit code of ``barman config-switch``.
        """
        cmd = ["barman", "config-switch"] + self._get_args()
        return self._run_subprocess(cmd)


class ConfigUpdateOperation(Operation):
    """
    Contain information and logic to process a config update operation.

    :cvar REQUIRED_ARGUMENTS: required arguments when creating a config update
        operation.
    :cvar TYPE: enum type of this operation.
    """

    REQUIRED_ARGUMENTS = ("changes",)
    TYPE = OperationType.CONFIG_UPDATE

    @classmethod
    def _validate_job_content(cls, content: Dict[str, Any]) -> None:
        """
        Validate the content of the job file before creating it.

        :param content: Python dictionary representing the JSON content of the
            job file.

        :raises:
            :exc:`MalformedContent`: if the set of options in *content* is
                either missing required keys.
        """
        required_args: Set[str] = set(cls.REQUIRED_ARGUMENTS)
        missing_args = required_args - set(content.keys())

        if missing_args:
            msg = (
                "Missing required arguments: "
                f"{', '.join(sorted(missing_args))}"
            )
            raise MalformedContent(msg)

    def write_job_file(self, content: Dict[str, Any]) -> None:
        """
        Write the job file with *content*.

        .. note::
            See :meth:`Operation.write_job_file` for more details.

        :param content: Python dictionary representing the JSON content of the
            job file. Besides what is contained in *content*, this method adds
            the following keys:

            * ``operation_type``: ``config_update``;
            * ``start_time``: current timestamp.
        """
        content["operation_type"] = self.TYPE.value
        content["start_time"] = self.time_event_now()
        self._validate_job_content(content)
        super().write_job_file(content)

    def _get_args(self) -> List[str]:
        """
        Get arguments for running ``barman config-update`` command.

        :return: list of arguments for ``barman config-update`` command.
        """
        job_content = self.read_job_file()

        json_changes = json.dumps(job_content.get("changes"))

        if TYPE_CHECKING:  # pragma: no cover
            assert isinstance(json_changes, str)

        return [json_changes]

    def _run_logic(
        self,
    ) -> Tuple[Union[str, bytearray, memoryview], Union[int, Any]]:
        """
        Logic to be ran when executing the config update operation.

        Run ``barman config-update`` command with the configured arguments.

        Will be called when running :meth:`Operation.run`.

        :return: a tuple consisting of:

            * ``stdout``/``stderr`` of ``barman config-update``;
            * exit code of ``barman config-update``.
        """
        cmd = ["barman", "config-update"] + self._get_args()
        return self._run_subprocess(cmd)


def main(callback: Callable[..., Any], *args: Tuple[Any, ...]) -> int:
    """
    Execute *callback* with *args* and log its output as an ``INFO`` message.

    .. note::
        If any issue is faced, log the exception as an ``ERROR`` message
        instead of logging the command output as an ``INFO`` message.

    :param callback: reference to any method from a :class:`ServerOperation`
        object.
    :return: ``-1`` if any issue is faced while executing *callback*, otherwise
        ``0``.
    """
    try:
        log.info(callback(args))
    except Exception as e:
        # TODO: we might behave differently depending upon the type here
        log.error(e)
        return -1

    return 0


if __name__ == "__main__":
    # If this module is run as the entry point, expose a command-line argument
    # parser. It exposes the same operations that are exposed through the REST
    # API, i.e., like list and get recovery operations.
    parser = argparse.ArgumentParser(
        description="Alternative to the REST API, so one can list, create and "
        "get information about jobs without a running REST API.",
    )
    parser.add_argument(
        "--server-name",
        help="Name of the Barman server related to the operation.",
    )
    parser.add_argument(
        "--operation-type",
        choices=[op_type.value for op_type in OperationType],
        default=OperationType.RECOVERY.value,
        help="Type of the operation. Optional for 'list-operations' command. "
        "Defaults to 'recovery' for 'get-operation' command.",
    )
    parser.add_argument(
        "--operation-id",
        help="ID of the operation, if you are trying to query an existing "
        "operation.",
    )
    parser.add_argument(
        "command",
        choices=["list-operations", "get-operation"],
        help="What we should do -- list operations, or get info about a "
        "specific operation.",
    )

    args = parser.parse_args()

    op_type = None

    if args.operation_type is not None:
        op_type = OperationType(args.operation_type)

    callback = None
    callback_args = None

    op_server = OperationServer(args.server_name)

    if args.command == "list-operations":
        callback = op_server.get_operations_list
        callback_args = (op_type,)
    elif args.command == "get-operation":
        if args.operation_id is None:
            raise RuntimeError(
                "'--operation-id' must be given when running "
                "'get-operation' command"
            )

        callback = op_server.get_operation_status
        callback_args = (args.operation_id,)

    retval = main(callback, callback_args)  # pyright: ignore
    sys.exit(retval)
