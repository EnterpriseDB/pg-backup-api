# -*- coding: utf-8 -*-
# © Copyright EnterpriseDB UK Limited 2021-2025 - All rights reserved.
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

"""Unit tests for the REST API endpoints."""
from distutils.version import StrictVersion
import json
import sys
from unittest.mock import Mock, MagicMock, patch

import flask
import pytest

from pg_backup_api.server_operation import (
    OperationServerConfigError,
    OperationNotExists,
    MalformedContent,
)


_HTTP_METHODS = {"DELETE", "GET", "PATCH", "POST", "PUT", "TRACE"}


@patch("pg_backup_api.server_operation.load_barman_config", MagicMock())
@patch(
    "pg_backup_api.logic.utility_controller.load_barman_config", MagicMock()
)
@patch("barman.__config__", MagicMock())
class TestUtilityController:
    """Run tests for the REST API endpoints."""

    @pytest.fixture(scope="module")
    def client(self):
        """Mock :mod:`barman.output` and get a Flask testing client.

        :yield: a Flask testing client.
        """
        with patch("pg_backup_api.run.load_barman_config", MagicMock()):
            from pg_backup_api.run import app

            app.config.update(
                {
                    "TESTING": True,
                }
            )

            from barman import output

            output.set_output_writer(output.AVAILABLE_WRITERS["json"]())

            with app.test_client() as test_client:
                with app.app_context():
                    yield test_client

    def _ensure_http_methods_not_allowed(self, methods, path, client):
        """Ensure none among *methods* are allowed when requesting *path*.

        :param methods: a set of methods to be tested.
        :param path: the URL path to be requested.
        :param client: a Flask testing client.
        """
        for method in methods:
            response = getattr(client, method.lower())(path)
            assert response.status_code == 405
            expected = b"The method is not allowed for the requested URL."
            assert expected in response.data

    @patch("pg_backup_api.logic.utility_controller.barman_diagnose", Mock())
    @patch.dict(
        "pg_backup_api.logic.utility_controller.output._writer.json_output",
        {
            "_INFO": ["SOME", "JSON", "ENTRIES", '{"global":{"config":{}}}'],
        },
    )
    def test_diagnose_ok(self, client):
        """Test ``/diagnose`` endpoint.

        Ensure a ``GET`` request returns ``200`` and the expected JSON output.
        """
        path = "/diagnose"

        response = client.get(path)

        assert response.status_code == 200
        assert response.data == b'{"global":{"config":{}}}\n'

    @patch("pg_backup_api.logic.utility_controller.barman_diagnose", Mock())
    @patch.dict(
        "pg_backup_api.logic.utility_controller.output._writer.json_output",
        {
            "_INFO": ["SOME", "JSON", "ENTRIES", '{"global":{"config":{}}}'],
        },
    )
    def test_diagnose_ok_old_barman(self, client):
        """Test ``/diagnose`` endpoint.

        Ensure a ``GET`` request returns ``200`` and the expected JSON output,
        even if using Barman 3.9 or older, in which case models implementation
        is not available.
        """
        path = "/diagnose"

        with patch("barman.__config__") as mock_config:
            mock_config.model_names.side_effect = AttributeError("Old Barman")
            response = client.get(path)

        assert response.status_code == 200
        assert response.data == b'{"global":{"config":{}}}\n'

    def test_diagnose_not_allowed(self, client):
        """Test ``/diagnose`` endpoint.

        Ensure all other HTTP request methods return an error.
        """
        path = "/diagnose"
        self._ensure_http_methods_not_allowed(
            _HTTP_METHODS - {"GET"}, path, client
        )

    def test_status_ok(self, client):
        """Test ``/status`` endpoint.

        Ensure a ``GET`` request returns ``200`` and the expected output.
        """
        path = "/status"

        response = client.get(path)

        assert response.status_code == 200
        assert response.data == b'"OK"'

    def test_status_not_allowed(self, client):
        """Test ``/status`` endpoint.

        Ensure all other HTTP request methods return an error.
        """
        path = "/status"

        self._ensure_http_methods_not_allowed(
            _HTTP_METHODS - {"GET"}, path, client
        )

    @pytest.mark.parametrize("status", ["IN_PROGRESS", "DONE", "FAILED"])
    @patch("pg_backup_api.logic.utility_controller.OperationServer")
    def test_servers_operation_id_get_ok(self, mock_op_server, status, client):
        """Test ``/servers/<SERVER_NAME>/operations/<OPERATION_ID>`` endpoint.

        Ensure a ``GET`` request returns ``200`` and the expected JSON output
        according to the status of the operation.
        """
        path = "/servers/SOME_SERVER_NAME/operations/SOME_OPERATION_ID"

        mock_op_server.return_value.config = object()
        mock_get_status = mock_op_server.return_value.get_operation_status

        mock_get_status.return_value = status

        response = client.get(path)

        mock_op_server.assert_called_once_with("SOME_SERVER_NAME")
        mock_get_status.assert_called_once_with("SOME_OPERATION_ID")

        assert response.status_code == 200
        expected = (
            '{"operation_id":"SOME_OPERATION_ID",' f'"status":"{status}"}}\n'
        ).encode()
        assert response.data == expected

    @patch("pg_backup_api.logic.utility_controller.OperationServer")
    def test_servers_operation_id_get_server_does_not_exist(
        self, mock_op_server, client
    ):
        """Test ``/servers/<SERVER_NAME>/operations/<OPERATION_ID>`` endpoint.

        Ensure ``GET`` returns ``404`` if the Barman server doesn't exist.
        """
        path = "/servers/SOME_SERVER_NAME/operations/SOME_OPERATION_ID"

        mock_op_server.side_effect = OperationServerConfigError("SOME_ISSUE")

        response = client.get(path)
        assert response.status_code == 404
        assert response.data == b'{"error":"404 Not Found: SOME_ISSUE"}\n'

    @patch("pg_backup_api.logic.utility_controller.OperationServer")
    def test_servers_operation_id_get_operation_does_not_exist(
        self, mock_op_server, client
    ):
        """Test ``/servers/<SERVER_NAME>/operations/<OPERATION_ID>`` endpoint.

        Ensure ``GET`` returns ``404`` if the operation doesn't exist.
        """
        path = "/servers/SOME_SERVER_NAME/operations/SOME_OPERATION_ID"

        mock_get_status = mock_op_server.return_value.get_operation_status
        mock_op_server.return_value.config = object()
        mock_get_status.side_effect = OperationNotExists("NOT_FOUND")

        response = client.get(path)
        assert response.status_code == 404
        expected = b'{"error":"404 Not Found: Resource not found"}\n'
        assert response.data == expected

    def test_servers_operation_id_get_not_allowed(self, client):
        """Test ``/servers/<SERVER_NAME>/operations/<OPERATION_ID>`` endpoint.

        Ensure all other HTTP request methods return an error.
        """
        path = "/servers/SOME_SERVER_NAME/operations/SOME_OPERATION_ID"
        self._ensure_http_methods_not_allowed(
            _HTTP_METHODS - {"GET"}, path, client
        )

    @pytest.mark.parametrize("status", ["IN_PROGRESS", "DONE", "FAILED"])
    @patch("pg_backup_api.logic.utility_controller.OperationServer")
    def test_instance_operation_id_get_ok(
        self, mock_op_server, status, client
    ):
        """Test ``/operations/<OPERATION_ID>`` endpoint.

        Ensure a ``GET`` request returns ``200`` and the expected JSON output
        according to the status of the operation.
        """
        path = "/operations/SOME_OPERATION_ID"

        mock_op_server.return_value.config = object()
        mock_get_status = mock_op_server.return_value.get_operation_status

        mock_get_status.return_value = status

        response = client.get(path)

        mock_op_server.assert_called_once_with(None)
        mock_get_status.assert_called_once_with("SOME_OPERATION_ID")

        assert response.status_code == 200
        expected = (
            '{"operation_id":"SOME_OPERATION_ID",' f'"status":"{status}"}}\n'
        ).encode()
        assert response.data == expected

    @patch("pg_backup_api.logic.utility_controller.OperationServer")
    def test_instance_operation_id_get_operation_does_not_exist(
        self, mock_op_server, client
    ):
        """Test ``/operations/<OPERATION_ID>`` endpoint.

        Ensure ``GET`` returns ``404`` if the operation doesn't exist.
        """
        path = "/operations/SOME_OPERATION_ID"

        mock_get_status = mock_op_server.return_value.get_operation_status
        mock_op_server.return_value.config = object()
        mock_get_status.side_effect = OperationNotExists("NOT_FOUND")

        response = client.get(path)
        assert response.status_code == 404
        expected = b'{"error":"404 Not Found: Resource not found"}\n'
        assert response.data == expected

    def test_instance_operation_id_get_not_allowed(self, client):
        """Test ``/operations/<OPERATION_ID>`` endpoint.

        Ensure all other HTTP request methods return an error.
        """
        path = "/operations/SOME_OPERATION_ID"
        self._ensure_http_methods_not_allowed(
            _HTTP_METHODS - {"GET"}, path, client
        )

    @patch("pg_backup_api.logic.utility_controller.OperationServer")
    def test_server_operation_get_ok(self, mock_op_server, client):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure a ``GET`` request returns ``200`` and the expected JSON output.
        """
        path = "/servers/SOME_SERVER_NAME/operations"

        mock_op_server.return_value.config = object()
        mock_get_ops = mock_op_server.return_value.get_operations_list
        mock_get_ops.return_value = [
            {
                "id": "SOME_ID_1",
                "type": "SOME_TYPE_1",
            },
            {
                "id": "SOME_ID_2",
                "type": "SOME_TYPE_2",
            },
        ]

        response = client.get(path)

        mock_op_server.assert_called_once_with("SOME_SERVER_NAME")
        mock_get_ops.assert_called_once_with()

        assert response.status_code == 200
        data = json.dumps({"operations": mock_get_ops.return_value})
        data = data.replace(" ", "") + "\n"
        expected = data.encode()
        assert response.data == expected

    @patch("pg_backup_api.logic.utility_controller.OperationServer")
    def test_server_operation_get_server_does_not_exist(
        self, mock_op_server, client
    ):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure ``GET`` request returns ``404`` if Barman server doesn't exist.
        """
        path = "/servers/SOME_SERVER_NAME/operations"

        mock_get_ops = mock_op_server.return_value.get_operations_list
        mock_op_server.side_effect = OperationServerConfigError("SOME_ISSUE")

        response = client.get(path)

        mock_op_server.assert_called_once_with("SOME_SERVER_NAME")
        mock_get_ops.assert_not_called()

        assert response.status_code == 404
        assert response.data == b'{"error":"404 Not Found: SOME_ISSUE"}\n'

    def test_server_operation_post_not_json(self, client):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure ``POST`` request won't work without data in JSON format.
        """
        path = "/servers/SOME_SERVER_NAME/operations"

        response = client.post(path, data={})

        expected_status_code = 415
        expected_data = b"Unsupported Media Type"
        version = sys.version_info

        # This is an issue which was detected while running tests through
        # GitHub Actions when using Python 3.7 and Flask 2.2.5. We might want
        # to remove this once we remove support for Python 3.7
        if (
            version.major <= 3
            and version.minor <= 7
            and StrictVersion(flask.__version__) <= StrictVersion("2.2.5")
        ):
            expected_status_code = 400
            expected_data = b"Bad Request"

        assert response.status_code == expected_status_code
        assert expected_data in response.data

    @patch("pg_backup_api.logic.utility_controller.OperationServer", Mock())
    @patch("pg_backup_api.logic.utility_controller.get_server_by_name")
    @patch("pg_backup_api.logic.utility_controller.OperationType")
    @patch("pg_backup_api.logic.utility_controller.parse_backup_id")
    @patch("pg_backup_api.logic.utility_controller.Server")
    @patch("pg_backup_api.logic.utility_controller.RecoveryOperation")
    @patch("subprocess.Popen")
    def test_server_operation_post_empty_json(
        self,
        mock_popen,
        mock_rec_op,
        mock_server,
        mock_parse_id,
        mock_op_type,
        mock_get_server,
        client,
    ):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure ``POST`` request returns ``400`` if JSON data is empty.
        """
        path = "/servers/SOME_SERVER_NAME/operations"

        response = client.post(path, json={})

        assert response.status_code == 400
        expected = (
            b"Minimum barman options not met for server "
            b"&#39;SOME_SERVER_NAME&#39;"
        )
        assert expected in response.data

        mock_get_server.assert_not_called()
        mock_op_type.assert_not_called()
        mock_parse_id.assert_not_called()
        mock_server.assert_not_called()
        mock_rec_op.assert_not_called()
        mock_popen.assert_not_called()

    @patch("pg_backup_api.logic.utility_controller.OperationServer", Mock())
    @patch("pg_backup_api.logic.utility_controller.get_server_by_name")
    @patch("pg_backup_api.logic.utility_controller.OperationType")
    @patch("pg_backup_api.logic.utility_controller.parse_backup_id")
    @patch("pg_backup_api.logic.utility_controller.Server")
    @patch("pg_backup_api.logic.utility_controller.RecoveryOperation")
    @patch("subprocess.Popen")
    def test_server_operation_post_server_rec_op_does_not_exist(
        self,
        mock_popen,
        mock_rec_op,
        mock_server,
        mock_parse_id,
        mock_op_type,
        mock_get_server,
        client,
    ):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure ``POST`` request returns ``404`` if Barman server doesn't exist
        when requesting a recovery operation.
        """
        path = "/servers/SOME_SERVER_NAME/operations"

        mock_get_server.return_value = None

        json_data = {
            "type": "recovery",
        }
        response = client.post(path, json=json_data)

        mock_get_server.assert_called_once_with("SOME_SERVER_NAME")
        mock_op_type.assert_not_called()
        mock_parse_id.assert_not_called()
        mock_server.assert_not_called()
        mock_rec_op.assert_not_called()
        mock_popen.assert_not_called()

        assert response.status_code == 404
        expected = (
            b'{"error":"404 Not Found: Server '
            b"'SOME_SERVER_NAME' does not exist\"}\n"
        )

        assert response.data == expected

    @patch("pg_backup_api.logic.utility_controller.OperationServer", Mock())
    @patch("pg_backup_api.logic.utility_controller.get_server_by_name")
    @patch("pg_backup_api.logic.utility_controller.OperationType")
    @patch("pg_backup_api.logic.utility_controller.parse_backup_id")
    @patch("pg_backup_api.logic.utility_controller.Server")
    @patch("pg_backup_api.logic.utility_controller.RecoveryOperation")
    @patch("subprocess.Popen")
    def test_server_operation_post_rec_op_backup_id_missing(
        self,
        mock_popen,
        mock_rec_op,
        mock_server,
        mock_parse_id,
        mock_op_type,
        mock_get_server,
        client,
    ):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure ``POST`` request returns ``400`` if ``backup_id`` is missing
        when requesting a recovery operation.
        """
        path = "/servers/SOME_SERVER_NAME/operations"
        json_data = {
            "type": "recovery",
        }

        mock_op_type.return_value = mock_op_type.RECOVERY

        response = client.post(path, json=json_data)

        mock_get_server.assert_called_once_with("SOME_SERVER_NAME")
        mock_op_type.assert_called_once_with("recovery")
        mock_parse_id.assert_not_called()
        mock_server.assert_not_called()
        mock_rec_op.assert_not_called()
        mock_popen.assert_not_called()

        assert response.status_code == 400
        assert b"Request body is missing ``backup_id``" in response.data

    @patch("pg_backup_api.logic.utility_controller.OperationServer", Mock())
    @patch("pg_backup_api.logic.utility_controller.get_server_by_name")
    @patch("pg_backup_api.logic.utility_controller.OperationType")
    @patch("pg_backup_api.logic.utility_controller.parse_backup_id")
    @patch("pg_backup_api.logic.utility_controller.Server")
    @patch("pg_backup_api.logic.utility_controller.RecoveryOperation")
    @patch("subprocess.Popen")
    def test_server_operation_post_rec_op_backup_does_not_exist(
        self,
        mock_popen,
        mock_rec_op,
        mock_server,
        mock_parse_id,
        mock_op_type,
        mock_get_server,
        client,
    ):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure ``POST`` request returns ``404`` if backup does not exist when
        requesting a recovery operation.
        """
        path = "/servers/SOME_SERVER_NAME/operations"
        json_data = {
            "type": "recovery",
            "backup_id": "SOME_BACKUP_ID",
        }

        mock_parse_id.return_value = None
        mock_op_type.return_value = mock_op_type.RECOVERY

        response = client.post(path, json=json_data)

        mock_get_server.assert_called_once_with("SOME_SERVER_NAME")
        mock_op_type.assert_called_once_with("recovery")
        mock_server.assert_called_once_with(mock_get_server.return_value)
        mock_parse_id.assert_called_once_with(
            mock_server.return_value, "SOME_BACKUP_ID"
        )
        mock_rec_op.assert_not_called()
        mock_popen.assert_not_called()

        assert response.status_code == 404
        expected = (
            b'{"error":"404 Not Found: Backup '
            b"'SOME_BACKUP_ID' does not exist\"}\n"
        )
        assert response.data == expected

    @patch("pg_backup_api.logic.utility_controller.OperationServer", Mock())
    @patch("pg_backup_api.logic.utility_controller.get_server_by_name")
    @patch("pg_backup_api.logic.utility_controller.OperationType")
    @patch("pg_backup_api.logic.utility_controller.parse_backup_id")
    @patch("pg_backup_api.logic.utility_controller.Server")
    @patch("pg_backup_api.logic.utility_controller.RecoveryOperation")
    @patch("subprocess.Popen")
    def test_server_operation_post_rec_op_missing_options(
        self,
        mock_popen,
        mock_rec_op,
        mock_server,
        mock_parse_id,
        mock_op_type,
        mock_get_server,
        client,
    ):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure ``POST`` request returns ``400`` if any option is missing when
        requesting a recovery operation.
        """
        path = "/servers/SOME_SERVER_NAME/operations"
        json_data = {
            "type": "recovery",
            "backup_id": "SOME_BACKUP_ID",
        }

        mock_op_type.return_value = mock_op_type.RECOVERY
        mock_parse_id.return_value = "SOME_BACKUP_ID"
        mock_rec_op.return_value.id = "SOME_OP_ID"
        mock_write_job = mock_rec_op.return_value.write_job_file
        mock_write_job.side_effect = MalformedContent("SOME_ERROR")

        response = client.post(path, json=json_data)

        mock_get_server.assert_called_once_with("SOME_SERVER_NAME")
        mock_op_type.assert_called_once_with("recovery")
        mock_server.assert_called_once_with(mock_get_server.return_value)
        mock_parse_id.assert_called_once_with(
            mock_server.return_value, "SOME_BACKUP_ID"
        )
        mock_rec_op.assert_called_once_with("SOME_SERVER_NAME")
        mock_write_job.assert_called_once_with(json_data)
        mock_popen.assert_not_called()

        assert response.status_code == 400
        expected = b"Make sure all options/arguments are met and try again"
        assert expected in response.data

    @patch("pg_backup_api.logic.utility_controller.OperationServer", Mock())
    @patch("pg_backup_api.logic.utility_controller.get_server_by_name")
    @patch("pg_backup_api.logic.utility_controller.OperationType")
    @patch("pg_backup_api.logic.utility_controller.ConfigSwitchOperation")
    @patch("subprocess.Popen")
    def test_server_operation_post_cs_op_missing_options(
        self, mock_popen, mock_cs_op, mock_op_type, mock_get_server, client
    ):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure ``POST`` request returns ``400`` if any option is missing when
        requesting a config switch operation.
        """
        path = "/servers/SOME_SERVER_NAME/operations"
        json_data = {
            "type": "config_switch",
        }

        mock_op_type.return_value = mock_op_type.CONFIG_SWITCH
        mock_cs_op.return_value.id = "SOME_OP_ID"
        mock_write_job = mock_cs_op.return_value.write_job_file
        mock_write_job.side_effect = MalformedContent("SOME_ERROR")

        response = client.post(path, json=json_data)

        mock_get_server.assert_called_once_with("SOME_SERVER_NAME")
        mock_op_type.assert_called_once_with("config_switch")
        mock_cs_op.assert_called_once_with("SOME_SERVER_NAME")
        mock_write_job.assert_called_once_with(json_data)
        mock_popen.assert_not_called()

        assert response.status_code == 400
        expected = b"Make sure all options/arguments are met and try again"
        assert expected in response.data

    @patch("pg_backup_api.logic.utility_controller.OperationServer", Mock())
    @patch("pg_backup_api.logic.utility_controller.get_server_by_name")
    @patch("pg_backup_api.logic.utility_controller.OperationType")
    @patch("pg_backup_api.logic.utility_controller.parse_backup_id")
    @patch("pg_backup_api.logic.utility_controller.Server")
    @patch("pg_backup_api.logic.utility_controller.RecoveryOperation")
    @patch("subprocess.Popen")
    def test_server_operation_post_rec_op_ok(
        self,
        mock_popen,
        mock_rec_op,
        mock_server,
        mock_parse_id,
        mock_op_type,
        mock_get_server,
        client,
    ):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure ``POST`` request returns ``202`` if everything is ok when
        requesting a recovery operation, and ensure the subprocess is started.
        """
        path = "/servers/SOME_SERVER_NAME/operations"
        json_data = {
            "type": "recovery",
            "backup_id": "SOME_BACKUP_ID",
        }

        mock_op_type.return_value = mock_op_type.RECOVERY
        mock_parse_id.return_value = "SOME_BACKUP_ID"
        mock_rec_op.return_value.id = "SOME_OP_ID"

        response = client.post(path, json=json_data)

        mock_write_job = mock_rec_op.return_value.write_job_file
        mock_get_server.assert_called_once_with("SOME_SERVER_NAME")
        mock_op_type.assert_called_once_with("recovery")
        mock_server.assert_called_once_with(mock_get_server.return_value)
        mock_parse_id.assert_called_once_with(
            mock_server.return_value, "SOME_BACKUP_ID"
        )
        mock_rec_op.assert_called_once_with("SOME_SERVER_NAME")
        mock_write_job.assert_called_once_with(json_data)
        mock_popen.assert_called_once_with(
            [
                "pg-backup-api",
                "recovery",
                "--server-name",
                "SOME_SERVER_NAME",
                "--operation-id",
                "SOME_OP_ID",
            ]
        )

        assert response.status_code == 202
        assert response.data == b'{"operation_id":"SOME_OP_ID"}\n'

    @patch("pg_backup_api.logic.utility_controller.OperationServer", Mock())
    @patch("pg_backup_api.logic.utility_controller.get_server_by_name")
    @patch("pg_backup_api.logic.utility_controller.OperationType")
    @patch("pg_backup_api.logic.utility_controller.ConfigSwitchOperation")
    @patch("subprocess.Popen")
    def test_server_operation_post_cs_op_ok(
        self, mock_popen, mock_cs_op, mock_op_type, mock_get_server, client
    ):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure ``POST`` request returns ``202`` if everything is ok when
        requesting a config switch operation, and ensure the subprocess is
        started.
        """
        path = "/servers/SOME_SERVER_NAME/operations"
        json_data = {
            "type": "config_switch",
        }

        mock_op_type.return_value = mock_op_type.CONFIG_SWITCH
        mock_cs_op.return_value.id = "SOME_OP_ID"

        response = client.post(path, json=json_data)

        mock_write_job = mock_cs_op.return_value.write_job_file
        mock_get_server.assert_called_once_with("SOME_SERVER_NAME")
        mock_op_type.assert_called_once_with("config_switch")
        mock_cs_op.assert_called_once_with("SOME_SERVER_NAME")
        mock_write_job.assert_called_once_with(json_data)
        mock_popen.assert_called_once_with(
            [
                "pg-backup-api",
                "config-switch",
                "--server-name",
                "SOME_SERVER_NAME",
                "--operation-id",
                "SOME_OP_ID",
            ]
        )

        assert response.status_code == 202
        assert response.data == b'{"operation_id":"SOME_OP_ID"}\n'

    @patch("pg_backup_api.logic.utility_controller.OperationServer", Mock())
    @patch("pg_backup_api.logic.utility_controller.get_server_by_name")
    @patch("pg_backup_api.logic.utility_controller.OperationType")
    @patch("pg_backup_api.logic.utility_controller.parse_backup_id")
    @patch("pg_backup_api.logic.utility_controller.Server")
    @patch("pg_backup_api.logic.utility_controller.RecoveryOperation")
    @patch("subprocess.Popen")
    def test_server_operation_post_ok_type_missing(
        self,
        mock_popen,
        mock_rec_op,
        mock_server,
        mock_parse_id,
        mock_op_type,
        mock_get_server,
        client,
    ):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure ``POST`` request returns ``202`` if everything is ok, and ensure
        the subprocess is started, even if ``type`` is absent, in which
        case it defaults to ``recovery``.
        """
        path = "/servers/SOME_SERVER_NAME/operations"
        json_data = {
            "backup_id": "SOME_BACKUP_ID",
        }

        mock_op_type.return_value = mock_op_type.RECOVERY
        mock_parse_id.return_value = "SOME_BACKUP_ID"
        mock_rec_op.return_value.id = "SOME_OP_ID"

        response = client.post(path, json=json_data)

        mock_write_job = mock_rec_op.return_value.write_job_file
        mock_get_server.assert_called_once_with("SOME_SERVER_NAME")
        mock_op_type.assert_called_once_with("recovery")
        mock_server.assert_called_once_with(mock_get_server.return_value)
        mock_parse_id.assert_called_once_with(
            mock_server.return_value, "SOME_BACKUP_ID"
        )
        mock_rec_op.assert_called_once_with("SOME_SERVER_NAME")
        mock_write_job.assert_called_once_with(json_data)
        mock_popen.assert_called_once_with(
            [
                "pg-backup-api",
                "recovery",
                "--server-name",
                "SOME_SERVER_NAME",
                "--operation-id",
                "SOME_OP_ID",
            ]
        )

        assert response.status_code == 202
        assert response.data == b'{"operation_id":"SOME_OP_ID"}\n'

    def test_server_operation_not_allowed(self, client):
        """Test ``/servers/<SERVER_NAME>/operations`` endpoint.

        Ensure all other HTTP request methods return an error.
        """
        path = "/servers/SOME_SERVER_NAME/operations"

        self._ensure_http_methods_not_allowed(
            _HTTP_METHODS - {"GET", "POST"}, path, client
        )

    @patch("pg_backup_api.logic.utility_controller.OperationServer")
    def test_instance_operation_get_ok(self, mock_op_server, client):
        """Test ``/operations`` endpoint.

        Ensure a ``GET`` request returns ``200`` and the expected JSON output.
        """
        path = "/operations"

        mock_op_server.return_value.config = object()
        mock_get_ops = mock_op_server.return_value.get_operations_list
        mock_get_ops.return_value = [
            {
                "id": "SOME_ID_1",
                "type": "SOME_TYPE_1",
            },
            {
                "id": "SOME_ID_2",
                "type": "SOME_TYPE_2",
            },
        ]

        response = client.get(path)

        mock_op_server.assert_called_once_with(None)
        mock_get_ops.assert_called_once_with()

        assert response.status_code == 200
        data = json.dumps({"operations": mock_get_ops.return_value})
        data = data.replace(" ", "") + "\n"
        expected = data.encode()
        assert response.data == expected

    def test_instance_operation_post_not_json(self, client):
        """Test ``/operations`` endpoint.

        Ensure ``POST`` request won't work without data in JSON format.
        """
        path = "/operations"

        response = client.post(path, data={})

        expected_status_code = 415
        expected_data = b"Unsupported Media Type"
        version = sys.version_info

        # This is an issue which was detected while running tests through
        # GitHub Actions when using Python 3.7 and Flask 2.2.5. We might want
        # to remove this once we remove support for Python 3.7
        if (
            version.major <= 3
            and version.minor <= 7
            and StrictVersion(flask.__version__) <= StrictVersion("2.2.5")
        ):
            expected_status_code = 400
            expected_data = b"Bad Request"

        assert response.status_code == expected_status_code
        assert expected_data in response.data

    @patch("pg_backup_api.logic.utility_controller.OperationServer", Mock())
    @patch("pg_backup_api.logic.utility_controller.OperationType")
    @patch("subprocess.Popen")
    def test_instance_operation_post_empty_json(
        self, mock_popen, mock_op_type, client
    ):
        """Test ``/operations`` endpoint.

        Ensure ``POST`` request returns ``400`` if JSON data is empty.
        """
        path = "/operations"

        response = client.post(path, json={})

        assert response.status_code == 400
        expected = b"Minimum barman options not met for instance operation"
        assert expected in response.data

        mock_op_type.assert_not_called()
        mock_popen.assert_not_called()

    @patch("pg_backup_api.logic.utility_controller.OperationServer", Mock())
    @patch("pg_backup_api.logic.utility_controller.OperationType")
    @patch("pg_backup_api.logic.utility_controller.ConfigUpdateOperation")
    @patch("subprocess.Popen")
    def test_instance_operation_post_cu_op_missing_options(
        self, mock_popen, mock_cu_op, mock_op_type, client
    ):
        """Test ``operations`` endpoint.

        Ensure ``POST`` request returns ``400`` if any option is missing when
        requesting a config update operation.
        """
        path = "operations"
        json_data = {
            "type": "config_update",
        }

        mock_op_type.return_value = mock_op_type.CONFIG_UPDATE
        mock_cu_op.return_value.id = "SOME_OP_ID"
        mock_write_job = mock_cu_op.return_value.write_job_file
        mock_write_job.side_effect = MalformedContent("SOME_ERROR")

        response = client.post(path, json=json_data)

        mock_op_type.assert_called_once_with("config_update")
        mock_cu_op.assert_called_once_with(None)
        mock_write_job.assert_called_once_with(json_data)
        mock_popen.assert_not_called()

        assert response.status_code == 400
        expected = b"Make sure all options/arguments are met and try again"
        assert expected in response.data

    @patch("pg_backup_api.logic.utility_controller.OperationServer", Mock())
    @patch("pg_backup_api.logic.utility_controller.OperationType")
    @patch("pg_backup_api.logic.utility_controller.ConfigUpdateOperation")
    @patch("subprocess.Popen")
    def test_instance_operation_post_cu_ok(
        self, mock_popen, mock_cu_op, mock_op_type, client
    ):
        """Test ``operations`` endpoint.

        Ensure ``POST`` request returns ``202`` if everything is ok when
        requesting a config-update operation, and ensure the subprocess is
        started.
        """
        path = "/operations"
        json_data = {
            "type": "config_update",
            "changes": "SOME_CHANGES",
        }

        mock_op_type.return_value = mock_op_type.CONFIG_UPDATE
        mock_cu_op.return_value.id = "SOME_OP_ID"

        response = client.post(path, json=json_data)

        mock_write_job = mock_cu_op.return_value.write_job_file
        mock_op_type.assert_called_once_with("config_update")
        mock_cu_op.assert_called_once_with(None)
        mock_write_job.assert_called_once_with(json_data)
        mock_popen.assert_called_once_with(
            ["pg-backup-api", "config-update", "--operation-id", "SOME_OP_ID"]
        )

        assert response.status_code == 202
        assert response.data == b'{"operation_id":"SOME_OP_ID"}\n'

    def test_instance_operation_not_allowed(self, client):
        """Test ``/operations`` endpoint.

        Ensure all other HTTP request methods return an error.
        """
        path = "/operations"

        self._ensure_http_methods_not_allowed(
            _HTTP_METHODS - {"GET", "POST"}, path, client
        )
