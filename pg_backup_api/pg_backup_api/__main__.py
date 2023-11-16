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

"""Implement pg-backup-api CLI main entry-point."""
import argparse
import sys

from pg_backup_api.run import (serve, status, recovery_operation,
                               config_switch_operation)


def main() -> None:
    """
    Main method of the Postgres Backup API app.

    Create the CLI of the tool, which can be used for:

    * Starting the REST API server -- ``pg-backup-api server``;
    * Checking the REST API server status -- ``pg-backup-api status``;
    * Running a ``barman recover`` operation -- ``pg-backup-api recovery``.
    """
    p = argparse.ArgumentParser(
        epilog="Postgres Backup API by EnterpriseDB (www.enterprisedb.com)"
    )

    subparsers = p.add_subparsers()

    p_serve = subparsers.add_parser(
        "serve",
        description="Start the REST API server. Listen for requests on "
                    "'127.0.0.1', on the given port.",
    )
    p_serve.add_argument("--port", type=int, default=7480,
                         help="Port to bind to.")
    p_serve.set_defaults(func=serve)

    p_status = subparsers.add_parser(
        "status",
        description="Check if the REST API server is up and running",
    )
    p_status.add_argument("--port", type=int, default=7480,
                          help="Port to be checked.")
    p_status.set_defaults(func=status)

    p_ops = subparsers.add_parser(
        "recovery",
        description="Perform a 'barman recover' through the 'pg-backup-api'. "
                    "Can only be run if a recover operation has been "
                    "previously registered."
    )
    p_ops.add_argument("--server-name", required=True,
                       help="Name of the Barman server to be recovered.")
    p_ops.add_argument("--operation-id", required=True,
                       help="ID of the operation in the 'pg-backup-api'.")
    p_ops.set_defaults(func=recovery_operation)

    p_ops = subparsers.add_parser(
        "config-switch",
        description="Perform a 'barman config switch' through the "
                    "'pg-backup-api'. Can only be run if a config switch "
                    "operation has been previously registered."
    )
    p_ops.add_argument("--server-name", required=True,
                       help="Name of the Barman server which config should be "
                            "switched.")
    p_ops.add_argument("--operation-id", required=True,
                       help="ID of the operation in the 'pg-backup-api'.")
    p_ops.set_defaults(func=config_switch_operation)

    args = p.parse_args()
    if hasattr(args, "func") is False:
        p.print_help()
        ret = True
    else:
        output, ret = args.func(args)

        if output:
            print(output)

    exit_code = 0 if ret is True else -1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
