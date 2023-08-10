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

import argparse
import sys

from pg_backup_api.run import serve, status, recovery_operation


def main():
    """
    Main method of the Postgres Backup API app
    """
    p = argparse.ArgumentParser(
        epilog="Postgres Backup API by EnterpriseDB (www.enterprisedb.com)"
    )

    subparsers = p.add_subparsers()

    p_serve = subparsers.add_parser("serve")
    p_serve.add_argument("--port", type=int, default=7480)
    p_serve.set_defaults(func=serve)

    p_status = subparsers.add_parser("status")
    p_status.add_argument("--port", type=int, default=7480)
    p_status.set_defaults(func=status)

    p_ops = subparsers.add_parser("recovery")
    p_ops.add_argument("--server-name", required=True)
    p_ops.add_argument("--operation-id", required=True)
    p_ops.set_defaults(func=recovery_operation)

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

