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

"""Unit tests for the CLI."""
import sys
from textwrap import dedent
from unittest.mock import MagicMock, patch

import pytest

from pg_backup_api.__main__ import main


_HELP_OUTPUT = {
    "pg-backup-api --help": dedent("""\
        usage: pg-backup-api [-h]
                             {serve,status,recovery,config-switch,config-update} ...

        positional arguments:
          {serve,status,recovery,config-switch,config-update}

        optional arguments:
          -h, --help            show this help message and exit

        Postgres Backup API by EnterpriseDB (www.enterprisedb.com)
\
    """),  # noqa: E501
    "pg-backup-api serve --help": dedent("""\
        usage: pg-backup-api serve [-h] [--port PORT]

        Start the REST API server. Listen for requests on '127.0.0.1', on the given
        port.

        optional arguments:
          -h, --help   show this help message and exit
          --port PORT  Port to bind to.
\
    """),  # noqa: E501
    "pg-backup-api status --help": dedent("""\
        usage: pg-backup-api status [-h] [--port PORT]

        Check if the REST API server is up and running

        optional arguments:
          -h, --help   show this help message and exit
          --port PORT  Port to be checked.
\
    """),  # noqa: E501
    "pg-backup-api recovery --help": dedent("""\
        usage: pg-backup-api recovery [-h] --server-name SERVER_NAME --operation-id
                                      OPERATION_ID

        Perform a 'barman recover' through the 'pg-backup-api'. Can only be run if a
        recover operation has been previously registered.

        optional arguments:
          -h, --help            show this help message and exit
          --server-name SERVER_NAME
                                Name of the Barman server to be recovered.
          --operation-id OPERATION_ID
                                ID of the operation in the 'pg-backup-api'.
\
    """),  # noqa: E501
    "pg-backup-api config-switch --help": dedent("""\
        usage: pg-backup-api config-switch [-h] --server-name SERVER_NAME
                                           --operation-id OPERATION_ID

        Perform a 'barman config switch' through the 'pg-backup-api'. Can only be run
        if a config switch operation has been previously registered.

        optional arguments:
          -h, --help            show this help message and exit
          --server-name SERVER_NAME
                                Name of the Barman server which config should be
                                switched.
          --operation-id OPERATION_ID
                                ID of the operation in the 'pg-backup-api'.
\
    """),  # noqa: E501
    "pg-backup-api config-update --help": dedent("""\
        usage: pg-backup-api config-update [-h] --operation-id OPERATION_ID

        Perform a 'barman config-update' through the 'pg-backup-api'. Can only be run
        if a config-update operation has been previously registered.

        optional arguments:
          -h, --help            show this help message and exit
          --operation-id OPERATION_ID
                                ID of the operation in the 'pg-backup-api'.
\
    """),  # noqa: E501
}

_COMMAND_FUNC = {
    "pg-backup-api serve": "serve",
    "pg-backup-api status": "status",
    "pg-backup-api recovery --server-name SOME_SERVER --operation-id SOME_OP_ID": "recovery_operation",  # noqa: E501
    "pg-backup-api config-switch --server-name SOME_SERVER --operation-id SOME_OP_ID": "config_switch_operation",  # noqa: E501
    "pg-backup-api config-update --operation-id SOME_OP_ID": "config_update_operation",  # noqa: E501
}


@pytest.mark.parametrize("command", _HELP_OUTPUT.keys())
@patch("shutil.get_terminal_size")
def test_main_helper(mock_term_size, command, capsys):
    """Test :func:`main`.

    Ensure all the ``--help`` calls print the expected content to the console.
    """
    # Get a predictable print size
    mock_term_size.return_value.columns = 80

    with patch("sys.argv", command.split()), pytest.raises(SystemExit) as exc:
        main()

    assert str(exc.value) == "0"

    expected = _HELP_OUTPUT[command]
    version = sys.version_info

    if version.major >= 3 and version.minor >= 10:
        expected = expected.replace("optional arguments:", "options:")

    assert capsys.readouterr().out == expected


@pytest.mark.parametrize("command", _COMMAND_FUNC.keys())
@pytest.mark.parametrize("output", [None, "SOME_OUTPUT"])
@pytest.mark.parametrize("success", [False, True])
def test_main_funcs(command, output, success, capsys):
    """Test :func:`main`.

    Ensure :func:`main` executes the expected functions, print the expected
    messages, and exits with the expected codes.
    """
    mock_controller = patch(f"pg_backup_api.__main__.{_COMMAND_FUNC[command]}")
    mock_func = mock_controller.start()

    mock_func.return_value = (output, success)

    with patch("sys.argv", command.split()), pytest.raises(SystemExit) as exc:
        main()

    mock_controller.stop()

    assert capsys.readouterr().out == (f"{output}\n" if output else "")
    assert str(exc.value) == ("0" if success else "-1")


@patch("argparse.ArgumentParser.parse_args")
def test_main_with_func(mock_parse_args, capsys):
    """Test :func:`main`.

    Ensure :func:`main` calls the function with the expected arguments, if a
    command has a function associated with it.
    """
    mock_parse_args.return_value.func = MagicMock()
    mock_func = mock_parse_args.return_value.func
    mock_func.return_value = ("SOME_OUTPUT", True)

    with pytest.raises(SystemExit) as exc:
        main()

    capsys.readouterr()  # so we don't write to stdout during unit tests

    mock_func.assert_called_once_with(mock_parse_args.return_value)
    assert str(exc.value) == "0"


@patch("argparse.ArgumentParser.print_help")
@patch("argparse.ArgumentParser.parse_args")
def test_main_without_func(mock_parse_args, mock_print_help, capsys):
    """Test :func:`main`.

    Ensure :func:`main` prints a helper if a command has no function associated
    with it.
    """
    delattr(mock_parse_args.return_value, "func")

    with pytest.raises(SystemExit) as exc:
        main()

    capsys.readouterr()  # so we don't write to stdout during unit tests

    mock_print_help.assert_called_once_with()
    assert str(exc.value) == "0"
