# -*- coding: utf-8 -*-
# © Copyright EnterpriseDB UK Limited 2021-2024 - All rights reserved.
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

"""Unit tests for functions used by the CLI."""

import argparse
from requests.exceptions import ConnectionError
from unittest.mock import MagicMock, patch, call

import pytest

from pg_backup_api.run import (serve, status, recovery_operation,
                               config_switch_operation,
                               config_update_operation)


@pytest.mark.parametrize("port", [7480, 7481])
@patch("pg_backup_api.run.output")
@patch("pg_backup_api.run.load_barman_config")
@patch("pg_backup_api.run.app")
def test_serve(mock_app, mock_load_config, mock_output, port):
    """Test :func:`serve`.

    Ensure :func:`serve` performs the expected calls and return the expected
    values.
    """
    mock_output.AVAILABLE_WRITERS.__getitem__.return_value = MagicMock()
    expected = mock_output.AVAILABLE_WRITERS.__getitem__.return_value
    expected.return_value = MagicMock()

    args = argparse.Namespace(port=port)

    assert serve(args) == (mock_app.run.return_value, True)

    mock_load_config.assert_called_once_with()
    mock_output.set_output_writer.assert_called_once_with(
        expected.return_value,
    )
    mock_app.run.assert_called_once_with(host="127.0.0.1", port=port)


@pytest.mark.parametrize("port", [7480, 7481])
@patch("requests.get")
def test_status_ok(mock_request, port):
    """Test :func:`status`.

    Ensure the expected ``GET`` request is performed, and that :func:`status`
    returns `OK` when the API is available.
    """
    args = argparse.Namespace(port=port)

    assert status(args) == ("OK", True)

    mock_request.assert_called_once_with(f"http://127.0.0.1:{port}/status")


@pytest.mark.parametrize("port", [7480, 7481])
@patch("requests.get")
def test_status_failed(mock_request, port):
    """Test :func:`status`.

    Ensure the expected ``GET`` request is performed, and that :func:`status`
    returns an error message when the API is not available.
    """
    args = argparse.Namespace(port=port)

    mock_request.side_effect = ConnectionError("Some Error")

    message = "The Postgres Backup API does not appear to be available."
    assert status(args) == (message, False)

    mock_request.assert_called_once_with(f"http://127.0.0.1:{port}/status")


@pytest.mark.parametrize("server_name", ["SERVER_1", "SERVER_2"])
@pytest.mark.parametrize("operation_id", ["OPERATION_1", "OPERATION_2"])
@pytest.mark.parametrize("rc", [0, 1])
@patch("pg_backup_api.run.RecoveryOperation")
def test_recovery_operation(mock_rec_op, server_name, operation_id, rc):
    """Test :func:`recovery_operation`.

    Ensure the operation is created and executed, and that the expected values
    are returned depending on the return code.
    """
    args = argparse.Namespace(server_name=server_name,
                              operation_id=operation_id)

    mock_rec_op.return_value.run.return_value = ("SOME_OUTPUT", rc)
    mock_write_output = mock_rec_op.return_value.write_output_file
    mock_time_event = mock_rec_op.return_value.time_event_now
    mock_read_job = mock_rec_op.return_value.read_job_file

    assert recovery_operation(args) == (mock_write_output.return_value,
                                        rc == 0)

    mock_rec_op.assert_called_once_with(server_name, operation_id)
    mock_rec_op.return_value.run.assert_called_once_with()
    mock_time_event.assert_called_once_with()
    mock_read_job.assert_called_once_with()

    # Make sure the expected content was added to `read_job_file` output before
    # writing it to the output file.
    assert len(mock_read_job.return_value.__setitem__.mock_calls) == 3
    mock_read_job.return_value.__setitem__.assert_has_calls([
        call('success', rc == 0),
        call('end_time', mock_time_event.return_value),
        call('output', "SOME_OUTPUT"),
    ])

    mock_write_output.assert_called_once_with(mock_read_job.return_value)


@pytest.mark.parametrize("server_name", ["SERVER_1", "SERVER_2"])
@pytest.mark.parametrize("operation_id", ["OPERATION_1", "OPERATION_2"])
@pytest.mark.parametrize("rc", [0, 1])
@patch("pg_backup_api.run.ConfigSwitchOperation")
def test_config_switch_operation(mock_cs_op, server_name, operation_id, rc):
    """Test :func:`config_switch_operation`.

    Ensure the operation is created and executed, and that the expected values
    are returned depending on the return code.
    """
    args = argparse.Namespace(server_name=server_name,
                              operation_id=operation_id)

    mock_cs_op.return_value.run.return_value = ("SOME_OUTPUT", rc)
    mock_write_output = mock_cs_op.return_value.write_output_file
    mock_time_event = mock_cs_op.return_value.time_event_now
    mock_read_job = mock_cs_op.return_value.read_job_file

    assert config_switch_operation(args) == (mock_write_output.return_value,
                                             rc == 0)

    mock_cs_op.assert_called_once_with(server_name, operation_id)
    mock_cs_op.return_value.run.assert_called_once_with()
    mock_time_event.assert_called_once_with()
    mock_read_job.assert_called_once_with()

    # Make sure the expected content was added to `read_job_file` output before
    # writing it to the output file.
    assert len(mock_read_job.return_value.__setitem__.mock_calls) == 3
    mock_read_job.return_value.__setitem__.assert_has_calls([
        call('success', rc == 0),
        call('end_time', mock_time_event.return_value),
        call('output', "SOME_OUTPUT"),
    ])

    mock_write_output.assert_called_once_with(mock_read_job.return_value)


@pytest.mark.parametrize("operation_id", ["OPERATION_1", "OPERATION_2"])
@pytest.mark.parametrize("rc", [0, 1])
@patch("pg_backup_api.run.ConfigUpdateOperation")
def test_config_update_operation(mock_cu_op, operation_id, rc):
    """Test :func:`config_update_operation`.

    Ensure the operation is created and executed, and that the expected values
    are returned depending on the return code.
    """
    args = argparse.Namespace(operation_id=operation_id)

    mock_cu_op.return_value.run.return_value = ("SOME_OUTPUT", rc)
    mock_write_output = mock_cu_op.return_value.write_output_file
    mock_time_event = mock_cu_op.return_value.time_event_now
    mock_read_job = mock_cu_op.return_value.read_job_file

    assert config_update_operation(args) == (mock_write_output.return_value,
                                             rc == 0)

    mock_cu_op.assert_called_once_with(None, operation_id)
    mock_cu_op.return_value.run.assert_called_once_with()
    mock_time_event.assert_called_once_with()
    mock_read_job.assert_called_once_with()

    # Make sure the expected content was added to `read_job_file` output before
    # writing it to the output file.
    assert len(mock_read_job.return_value.__setitem__.mock_calls) == 3
    mock_read_job.return_value.__setitem__.assert_has_calls([
        call('success', rc == 0),
        call('end_time', mock_time_event.return_value),
        call('output', "SOME_OUTPUT"),
    ])

    mock_write_output.assert_called_once_with(mock_read_job.return_value)
