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
Implement pg-backup-api CLI commands.

:var app: the Flask application instance.
"""
import requests
import subprocess
from typing import Dict, List, Tuple, Union, TYPE_CHECKING

from requests.exceptions import ConnectionError

from barman import output

from pg_backup_api.utils import (
    API_CONFIG,
    create_app,
    load_barman_config,
)
from pg_backup_api.server_operation import ServerOperation


if TYPE_CHECKING:  # pragma: no cover
    import argparse

app = create_app()


def serve(args: argparse.Namespace) -> Tuple[None, bool]:
    """
    Run the Postgres Backup API app.

    Load Barman configuration, set up Barman JSON console output writer and
    listen to requests on ``127.0.0.1``, on the given port.

    :param args: command-line arguments for ``pg-backup-api serve`` command.
        Contains the ``port`` to listen on.
    :return: a tuple consisting of two items:

        * ``None`` -- output of :meth:`flask.app.Flask.run`;
        * ``True`` to indicate an successful operation.
    """
    # TODO determine backup tool setup based on config
    # load barman configs/setup barman for the app
    load_barman_config()
    output.set_output_writer(output.AVAILABLE_WRITERS["json"]())

    # bc currently only the PEM agent will be connecting, only run on localhost
    run = app.run(host="127.0.0.1", port=args.port)
    return (run, True)


def status(args: argparse.Namespace) -> Tuple[str, bool]:
    """
    Check Postgres Backup API app status.

    :param args: command-line arguments for ``pg-backup-api status`` command.
        Contains the ``port`` to be checked for app availability.
    :return: a tuple consisting of two items:

        * status: ``OK`` if up and running, an error message otherwise;
        * ``True`` is status is ``OK``, ``False`` otherwise
    """
    message = "OK"
    try:
        requests.get(f"http://127.0.0.1:{args.port}/status")
    except ConnectionError:
        message = "The Postgres Backup API does not appear to be available."

    return (message, True if message == "OK" else False)


def run_and_return_barman_recover(options: List[str], barman_args: List[str]) \
        -> Tuple[Union[bytes, str], int]:
    """
    Run ``barman recover`` and wait for it to complete.

    :param options: optional command-line arguments for ``barman recover``
        command.
    :param barman_args: positional command-line arguments for
        ``barman recover`` command (server name, backup ID, and destination
        directory).
    :return: a tuple consisting of 2 items related to ``barman recover``
        execution:

        * Content of ``stdout``/``stderr``;
        * Exit code.
    """
    cmd = "barman recover".split() + options + barman_args
    process = subprocess.Popen(cmd, stderr=subprocess.STDOUT,
                               stdout=subprocess.PIPE)
    stdout, _ = process.communicate()

    return (stdout, process.returncode)


def extract_options_from_file(jobfile_content: Dict[str, str]) -> List[str]:
    """
    Get list of options to be used as arguments for ``barman recover``.

    :param jobfile_content: content of the JSON file created by pg-backup-api
        for an operation parsed as a Python :class:`dict` instance.
    :return: list of positional arguments to be passed to ``barman recover``
        command. Only consider options listed in ``supported_options`` key of
            :data:`pg_backup_api.utils.API_CONFIG`.
    """
    options = []
    available_keys = jobfile_content.keys()
    for option_name in API_CONFIG["supported_options"]:
        if option_name in available_keys:
            cmd_option = option_name.replace("_", "-")
            options.append(f"--{cmd_option}")
            options.append(jobfile_content[option_name])
    return options


def recovery_operation(args: argparse.Namespace) -> Tuple[None, bool]:
    """
    Perform a ``barman recover`` through the pg-backup-api.

    .. note::
        Can only be run if a recover operation has been previously registered.

    Besides the required positional arguments of ``barman recover``, we can
    also provide additional options to that command. See
    :func:`extract_options_from_file`.

    In the end of execution creates an output file through
    :meth:`pg_backup_api.server_operation.ServerOperation.create_output_file`
    with the following content:

    * ``success``: if the operation succeeded or not;
    * ``end_time``: timestamp when the operation finished;
    * ``output``: ``stdout``/``stderr`` of the operation.

    :param args: command-line arguments for ``pg-backup-api recovery`` command.
        Contains the name of the Barman server related to the operation.
    :return: a tuple consisting of two items:

        * ``None`` -- output of :meth:`ServerOperation.create_output_file`;
        * ``True`` if ``barman recover`` was successful, ``False`` otherwise.
    """
    server_ops = ServerOperation(args.server_name, args.operation_id)
    content = server_ops.get_job_file_content()

    options = extract_options_from_file(content)

    barman_args = []
    barman_args.append(args.server_name)
    barman_args.append(content["backup_id"])
    barman_args.append(content["destination_directory"])

    output, retcode = run_and_return_barman_recover(options, barman_args)
    output = output.decode() if isinstance(output, bytes) else output
    success = True
    if retcode:
        success = False

    end_time = server_ops.time_event_now()
    content["success"] = success
    content["end_time"] = end_time
    content["output"] = output

    return (server_ops.create_output_file(content), success)
