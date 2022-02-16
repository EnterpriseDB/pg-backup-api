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

import json

import barman
from barman import diagnose, output
from barman.server import Server
from pg_backup_api.openapi_server.util import deserialize_model
from pg_backup_api.openapi_server.models.diagnose_output import DiagnoseOutput


class UtilityController:
    def diagnose(self):
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

        diagnose.exec_diagnose(server_dict, errors_list)

        # new outputs are appended, so grab the last one
        stored_output = json.loads(output._writer.json_output["_INFO"][-1])

        diag_output = deserialize_model(stored_output, DiagnoseOutput)

        return diag_output

    def status(self):
        return "OK"  # If this app isn't running, we obviously won't return!
