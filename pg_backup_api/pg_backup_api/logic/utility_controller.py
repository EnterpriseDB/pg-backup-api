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

"""Define the Flask endpoints of the pg-backup-api REST API server."""
import json
import subprocess
from typing import Any, Dict, Tuple, Union, TYPE_CHECKING

from flask import abort, jsonify, request

import barman
from barman import diagnose as barman_diagnose, output
from barman.server import Server

from pg_backup_api.utils import (load_barman_config, get_server_by_name,
                                 parse_backup_id)

from pg_backup_api.run import app
from pg_backup_api.server_operation import (OperationServer,
                                            OperationServerConfigError,
                                            OperationType,
                                            DEFAULT_OP_TYPE,
                                            RecoveryOperation,
                                            ConfigSwitchOperation,
                                            MalformedContent)

if TYPE_CHECKING:  # pragma: no cover
    from flask import Request, Response
    from barman.config import Config as BarmanConfig
    from pg_backup_api.server_operation import Operation


@app.route("/diagnose", methods=["GET"])
def diagnose() -> 'Response':
    """
    Handle ``GET`` request to ``/diagnose``.

    Get ``barman diagnose`` output.

    :return: a response containing ``barman diagnose`` output in JSON format.
    """
    # Reload the barman config so that any changes are picked up
    load_barman_config()

    if TYPE_CHECKING:  # pragma: no cover
        assert isinstance(barman.__config__, BarmanConfig)

    # Get every server (both inactive and temporarily disabled)
    servers = barman.__config__.server_names()

    server_dict = {}
    for server in servers:  # pyright: ignore
        conf = barman.__config__.get_server(server)
        if conf is None:
            # Unknown server
            server_dict[server] = None
        else:
            server_dict[server] = Server(conf)

    # errors list with duplicate paths between servers
    errors_list = barman.__config__.servers_msg_list

    barman_diagnose.exec_diagnose(server_dict, errors_list)

    # new outputs are appended, so grab the last one
    stored_output = json.loads(output._writer.json_output["_INFO"][-1])

    # clear the output writer dict
    output._writer.json_output = {}

    return jsonify(stored_output)


@app.route("/status", methods=["GET"])
def status() -> str:
    """
    Handle ``GET`` request to ``/status``.

    Check if REST API server is up and running.

    :return: an `"OK"` response if up and running.
    """
    return '"OK"'  # If this app isn't running, we obviously won't return!


@app.errorhandler(404)
def resource_not_found(error: Any) -> Tuple['Response', int]:
    """
    Configure a handler for HTTP 404 responses.

    :param error: error message for the response.
    :return: a tuple consisting of:

        * JSON response with an ``error`` key containing the error;
        * ``404`` to indicate an HTTP 404 response.
    """
    return jsonify(error=str(error)), 404


@app.route("/servers/<server_name>/operations/<operation_id>")
def servers_operation_id_get(server_name: str, operation_id: str) \
        -> 'Response':
    """
    ``GET`` request to ``/servers/*server_name*/operations/*operation_id*``.

    Get status of an operation with ID *operation_id* for Barman server named
    *server_name*.

    :param server_name: name of the Barman server related to the operation.
    :param operation_id: ID of the operation previously created through
        pg-backup-api.
    :return: if *server_name* and *operation_id* are valid, return a JSON
        response containing these keys:

        * ``operation_id``: the same as *operation_id*;
        * ``status``: status of the operation. Maybe be one among: ``DONE``,
          ``FAILED`` or ``IN_PROGRESS``.

        If either *server_name* or *operation_id* is invalid -- or both --
        return a HTTP 400 response with the relevant error message.
    """
    try:
        op_server = OperationServer(server_name)
        status = op_server.get_operation_status(operation_id)
        response = {"operation_id": operation_id, "status": status}

        return jsonify(response)
    except OperationServerConfigError as e:
        abort(404, description=str(e))
    except Exception:
        abort(404, description="Resource not found")


def servers_operations_post(server_name: str,
                            request: 'Request') -> Dict[str, str]:
    """
    Handle ``POST`` request to ``/servers/*server_name*/operations``.

    :param server_name: name of the Barman server for which a operation will be
        created.
    :param request: the flask request that has been received by the routing
        function.

        Should contain a JSON body with a key ``type``, which identified the
        type of the operation. The rest of the content depends on the type of
        operation being requested:

        * ``recovery``:

            * ``backup_id``: ID of the backup to be recovered;
            * ``destination_directory``: where to restore the backup in the
              target machine;
            * ``remote_ssh_command``: SSH command to connect to the target
              machine.

        * ``config_switch`` -- TODO: update arguments:

            * ``to``: some argument;
            * ``be``: some other argument;
            * ``defined``: some other argument.

    :return: if *server_name* and the JSON body informed through the
        ``POST`` request are valid, return a JSON response containing a key
        ``operation_id`` with the ID of the operation that has been created.

        Otherwise, if any issue is identified, return a response with either of
        the following statuses and the relevant error message:

        * ``400``: if any required option is missing in the JSON request body.
        * ``404``: if either *server_name* or any value in the JSON request
            body is invalid.
    """
    request_body = request.get_json()

    if not request_body:
        msg_400 = f"Minimum barman options not met for server '{server_name}'"
        abort(400, description=msg_400)

    server = get_server_by_name(server_name)

    if not server:
        msg_404 = f"Server '{server_name}' does not exist"
        abort(404, description=msg_404)

    operation = None
    cmd = None
    op_type = OperationType(request_body.get("type", DEFAULT_OP_TYPE.value))

    if op_type == OperationType.RECOVERY:
        try:
            msg_backup_id = request_body["backup_id"]
        except KeyError:
            msg_400 = "Request body is missing ``backup_id``"
            abort(400, description=msg_400)

        backup_id = parse_backup_id(Server(server), msg_backup_id)

        if not backup_id:
            msg_404 = f"Backup '{msg_backup_id}' does not exist"
            abort(404, description=msg_404)

        operation = RecoveryOperation(server_name)
        cmd = f"pg-backup-api recovery --server-name {server_name}"
    elif op_type == OperationType.CONFIG_SWITCH:
        # TODO: define the logic for performing a config switch operation
        operation = ConfigSwitchOperation(server_name)
        cmd = f"pg-backup-api config-switch --server-name {server_name}"

    if TYPE_CHECKING:  # pragma: no cover
        assert isinstance(operation, Operation)
        assert isinstance(cmd, str)

    try:
        operation.write_job_file(request_body)
    except MalformedContent:
        msg_400 = "Make sure all options/arguments are met and try again"
        abort(400, description=msg_400)

    cmd += f" --operation-id {operation.id}"
    subprocess.Popen(cmd.split())

    return {"operation_id": operation.id}


@app.route("/servers/<server_name>/operations", methods=("GET", "POST"))
def server_operation(server_name: str) \
        -> Union[Tuple['Response', int], 'Response']:
    """
    Handle ``GET``/``POST`` request to ``/servers/*server_name*/operations``.

    Get a list of operations for *server_name*, if a ``GET`` request, or create
    a new operation for *server_name*, if a ``POST`` request.

    :param server_name: name of the Barman server related to the operation(s).

    :return: the returned response varies:

        * If a successful ``GET`` request, then return a JSON response with
          ``operations`` key containing a list of operations for Barman server
          *server_name*. Each item in the list contain the operation ID and the
          operation type;
        * If a successful ``POST`` request, then return a JSON response with
          HTTP status ``202`` containing an ``operation_id`` key with the ID
          of the operation that has been created for the Barman server
          *server_name*;
        * If any issue is faced when processing the request, return an HTTP
          ``400`` or ``404`` response with the relevant error message.
    """
    if request.method == "POST":
        return jsonify(servers_operations_post(server_name, request)), 202

    try:
        operation = OperationServer(server_name)
        available_operations = {"operations": operation.get_operations_list()}
        return jsonify(available_operations)
    except OperationServerConfigError as e:
        abort(404, description=str(e))
