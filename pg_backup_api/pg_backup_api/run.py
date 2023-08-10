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


import requests
import subprocess

from requests.exceptions import ConnectionError

from barman import output

from pg_backup_api.utils import (
    API_CONFIG,
    create_app,
    load_barman_config,
)
from pg_backup_api.server_operation import ServerOperation

app = create_app()


def serve(args):
    """
    Run the Postgres Backup API app.
    """
    # TODO determine backup tool setup based on config
    # load barman configs/setup barman for the app
    load_barman_config()
    output.set_output_writer(output.AVAILABLE_WRITERS["json"]())

    # bc currently only the PEM agent will be connecting, only run on localhost
    run = app.run(host="127.0.0.1", port=args.port)
    return (run, True)


def status(args):
    message = "OK"
    try:
        requests.get("http://127.0.0.1:{args.port}/status".format(args=args))
    except ConnectionError:
        message = "The Postgres Backup API does not appear to be available."

    return (message, True if message == "OK" else False)


def run_and_return_barman_recover(options, barman_args):
    cmd = "barman recover".split() + options + barman_args
    process = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    stdout, _ = process.communicate()

    return (stdout, process.returncode)


def extract_options_from_file(jobfile_content):
    options = []
    available_keys = jobfile_content.keys()
    for option_name in API_CONFIG["supported_options"]:
        if option_name in available_keys:
            cmd_option = option_name.replace("_", "-")
            options.append("--{}".format(cmd_option))
            options.append(jobfile_content[option_name])
    return options


def recovery_operation(args):
    server_ops = ServerOperation(args.server_name, args.operation_id)
    content = server_ops.get_job_file_content()

    options = extract_options_from_file(content)

    barman_args = []
    barman_args.append(args.server_name)
    barman_args.append(content["backup_id"])
    barman_args.append(content["destination_directory"])

    output, retcode = run_and_return_barman_recover(options, barman_args)
    success = True
    if retcode:
        success = False

    end_time = server_ops.time_event_now()
    content["success"] = success
    content["end_time"] = end_time
    content["output"] = output.decode() if isinstance(output, bytes) else output

    return (server_ops.create_output_file(content), success)
