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

import datetime
import json
import subprocess

from flask import abort, jsonify, request

import barman
from barman import diagnose as barman_diagnose, output
from barman.server import Server

from pg_backup_api.utils import load_barman_config, get_server_by_name

from pg_backup_api.run import app


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
    abort(404, description="Resource not found")


@app.route("/servers/<server_name>/operations")
def servers_operations_get(server_name):
    message_404 = "'{}' does not exist".format(server_name)
    abort(404, description=message_404)


def servers_operations_post(server_name):
    backup_id = None
    request_body = request.get_json()
    server = get_server_by_name(server_name)

    if server:
        server_object = Server(server)
        backup_id = server_object.get_backup(backup_id)

    if not server or not backup_id:
        message_404 = "Server '{}' and/or Backup '{}' does not exist"\
                .format(server_name, backup_id)
        abort(404, description=message_404)

    operation_id = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    cmd = "pg-backup-api recovery --server-name {} --operation-id {}".format(
            server_name,
            operation_id)
    subprocess.Popen(cmd.split())
    return { "operation_id": operation_id }


@app.route("/servers/<server_name>/operations", methods=('GET', 'POST'))
def server_operation(server_name):
    if request.method == 'POST':
        return servers_operations_post(server_name)
