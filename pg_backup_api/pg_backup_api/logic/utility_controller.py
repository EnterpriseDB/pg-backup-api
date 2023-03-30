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

import datetime
import json
import subprocess

from flask import abort, jsonify, request

import barman
from barman import diagnose as barman_diagnose, output
from barman.server import Server

from pg_backup_api.utils import load_barman_config, get_server_by_name

from pg_backup_api.run import app
from pg_backup_api.server_operation import ServerOperation, ServerOperationConfigError


@app.route("/diagnose", methods=["GET"])
def diagnose():
    # Reload the barman config so that any changes are picked up
    load_barman_config()
    # Get every server (both inactive and temporarily disabled)
    servers = barman.__config__.server_names()

    server_dict = {}
    for server in servers:
        conf = barman.__config__.get_server(server)
        if conf is None:
            # Unknown server
            server_dict[server] = None
        else:
            server_object = Server(conf)
            server_dict[server] = server_object

    # errors list with duplicate paths between servers
    errors_list = barman.__config__.servers_msg_list

    barman_diagnose.exec_diagnose(server_dict, errors_list)

    # new outputs are appended, so grab the last one
    stored_output = json.loads(output._writer.json_output["_INFO"][-1])

    # clear the output writer dict
    output._writer.json_output = {}

    return jsonify(stored_output)


@app.route("/status", methods=["GET"])
def status():
    return '"OK"'  # If this app isn't running, we obviously won't return!


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify(error=str(error)), 404


@app.route("/servers/<server_name>/operations/<operation_id>")
def servers_operation_id_get(server_name, operation_id):
    try:
        operation = ServerOperation(server_name, operation_id)
        status = operation.get_status_by_operation_id()
        response = {"recovery_id": operation_id, "status": status}

        return jsonify(response)
    except ServerOperationConfigError as e:
        abort(404, description=str(e))
    except Exception:
        abort(404, description="Resource not found")


def servers_operations_post(server_name, request):
    request_body = request.get_json()
    if not request_body:
        message_400 = "Minimum barman options not met for server '{}'".format(
            server_name
        )
        abort(400, description=message_400)

    server = get_server_by_name(server_name)

    if not server:
        message_404 = "Server '{}' does not exist".format(server_name)
        abort(404, description=message_404)

    backup_id = request_body["backup_id"]
    server_object = Server(server)
    if not server_object.get_backup(backup_id):
        message_404 = "Backup '{}' does not exist".format(backup_id)
        abort(404, description=message_404)

    operation_id = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    operation = ServerOperation(server_name, operation_id=operation_id)

    try:
        operation.write_jobs_files(request_body)
    except KeyError:
        message_400 = "Make sure all options/arguments are met and try again"
        abort(400, description=message_400)

    cmd = "pg-backup-api recovery --server-name {} --operation-id {}".format(
        server_name, operation_id
    )
    subprocess.Popen(cmd.split())
    return {"operation_id": operation_id}


@app.route("/servers/<server_name>/operations", methods=("GET", "POST"))
def server_operation(server_name):
    if request.method == "POST":
        return jsonify(servers_operations_post(server_name, request)), 202

    try:
        operation = ServerOperation(server_name)
        available_operations = {"operations": operation.get_operations_list()}
        return jsonify(available_operations)
    except ServerOperationConfigError as e:
        abort(404, description=str(e))
