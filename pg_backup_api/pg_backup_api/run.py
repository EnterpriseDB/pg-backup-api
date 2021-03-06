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


import argparse
import connexion
import logging
from logging.config import dictConfig
import requests
from requests.exceptions import ConnectionError

import barman
from barman import config, output
from pg_backup_api.openapi_server import encoder


LOG_FILENAME = "/var/log/barman/barman-api.log"  # TODO make configurable


def serve(args):
    """
    Run the Postgres Backup API app.
    """
    # TODO determine backup tool setup based on config
    # load barman configs/setup barman for the app
    cfg = config.Config("/etc/barman.conf")
    barman.__config__ = cfg
    cfg.load_configuration_files_directory()
    output.set_output_writer(output.AVAILABLE_WRITERS["json"]())

    # setup and run the app
    app = connexion.App(__name__, specification_dir="./spec/")
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api(
        "pg_backup_api.yaml", arguments={"title": "Postgres Backup API"}, pythonic_params=True
    )

    # bc currently only the PEM agent will be connecting, only run on localhost
    app.run(host="127.0.0.1", port=args.port)


def status(args):
    try:
        requests.get(f"http://127.0.0.1:{args.port}/status")
    except ConnectionError:
        return "The Postgres Backup API does not appear to be available."
    return "OK"


def main():
    """
    Main method of the Postgres Backup API API app
    """
    # setup logging
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s:%(module)s: %(message)s",
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.FileHandler",
                    "filename": LOG_FILENAME,
                    "formatter": "default",
                }
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
        }
    )
    logger = logging.getLogger(__name__)

    p = argparse.ArgumentParser(epilog="Postgres Backup API by EnterpriseDB (www.enterprisedb.com)")

    subparsers = p.add_subparsers()

    p_serve = subparsers.add_parser('serve')
    p_serve.add_argument('--port', type=int, default=7480)
    p_serve.set_defaults(func=serve)

    p_status = subparsers.add_parser('status')
    p_status.add_argument('--port', type=int, default=7480)
    p_status.set_defaults(func=status)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    main()
