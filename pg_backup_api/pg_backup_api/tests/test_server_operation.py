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

"""Unit tests for the classes related with REST API operations."""
import os
import subprocess
from unittest.mock import Mock, MagicMock, call, patch

import pytest

from pg_backup_api.server_operation import (
    OperationServer,
    MalformedContent,
    OperationType,
    OperationNotExists,
    Operation,
    RecoveryOperation,
)


_BARMAN_HOME = "/BARMAN/HOME"
_BARMAN_SERVER = "BARMAR_SERVER"


class TestOperationServer:
    """Run tests for :class:`OperationServer`."""

    @pytest.fixture
    @patch("pg_backup_api.server_operation.get_server_by_name", Mock())
    @patch("pg_backup_api.server_operation.load_barman_config", Mock())
    @patch.object(OperationServer, "_create_dir", Mock())
    def op_server(self):
        """Create a :class:`OperationServer` instance for testing.

        :return: :class:`OperationServer` instance for testing.
        """
        with patch("barman.__config__") as mock_config:
            mock_config.barman_home = _BARMAN_HOME
            return OperationServer(_BARMAN_SERVER)

    def test___init__(self, op_server):
        """Test :meth:`OperationServer.__init__`.

        Ensure its attributes are set as expected.
        """
        # Ensure name is as expected.
        assert op_server.name == _BARMAN_SERVER

        # Ensure "jobs" directory is created in expected path.
        expected = os.path.join(_BARMAN_HOME, _BARMAN_SERVER, "jobs")
        assert op_server.jobs_basedir == expected

        # Ensure "output" directory is created in the expected path.
        expected = os.path.join(_BARMAN_HOME, _BARMAN_SERVER, "output")
        assert op_server.output_basedir == expected

    @patch("os.path.isdir")
    @patch("os.path.exists")
    def test__create_dir_file_exists(self, mock_exists, mock_isdir, op_server):
        """Test :meth:`OperationServer._create_dir`.

        Ensure an exception is raised if the path already exists as a file.
        """
        dir_path = "/SOME/DIR"

        mock_exists.return_value = True
        mock_isdir.return_value = False

        with pytest.raises(NotADirectoryError) as exc:
            op_server._create_dir(dir_path)

        mock_exists.assert_called_once_with(dir_path)
        mock_isdir.assert_called_once_with(dir_path)

        expected = f"'{dir_path}' exists but it is not a directory"
        assert str(exc.value) == expected

    @patch("os.path.isdir")
    @patch("os.path.exists")
    def test__create_dir_directory_exists(self, mock_exists, mock_isdir,
                                          op_server):
        """Test :meth:`OperationServer._create_dir`.

        Ensure no exception occurs if the directory already exists.
        """
        dir_path = "/SOME/DIR"

        mock_exists.return_value = True
        mock_isdir.return_value = True

        op_server._create_dir(dir_path)

        mock_exists.assert_called_once_with(dir_path)
        mock_isdir.assert_called_once_with(dir_path)

    @patch("os.makedirs")
    @patch("os.path.isdir")
    @patch("os.path.exists")
    def test__create_dir_ok(self, mock_exists, mock_isdir, mock_makedirs,
                            op_server):
        """Test :meth:`OperationServer._create_dir`.

        Ensure the directory is created if it's missing.
        """
        dir_path = "/SOME/DIR"

        mock_exists.return_value = False

        op_server._create_dir(dir_path)

        mock_exists.assert_called_once_with(dir_path)
        mock_isdir.assert_not_called()
        mock_makedirs.assert_called_once_with(dir_path)

    def test__create_jobs_dir(self, op_server):
        """Test :meth:`OperationServer._create_jobs_dir`.

        Ensure :meth:`OperationServer._create_dir` is called as expected.
        """
        with patch.object(op_server, "_create_dir") as mock_create_dir:
            op_server._create_jobs_dir()
            mock_create_dir.assert_called_once_with(op_server.jobs_basedir)

    def test__create_output_dir(self, op_server):
        """Test :meth:`OperationServer._create_output_dir`.

        Ensure :meth:`OperationServer._create_dir` is called as expected.
        """
        with patch.object(op_server, "_create_dir") as mock_create_dir:
            op_server._create_output_dir()
            mock_create_dir.assert_called_once_with(op_server.output_basedir)

    def test_get_job_file_path(self, op_server):
        """Test :meth:`OperationServer.get_job_file_path`.

        Ensure it returns the expected file path.
        """
        id = "SOME_OP_ID"

        expected = os.path.join(op_server.jobs_basedir, f"{id}.json")
        assert op_server.get_job_file_path(id) == expected

    def test_get_output_file_path(self, op_server):
        """Test :meth:`OperationServer.get_output_file_path`.

        Ensure it returns the expected file path.
        """
        id = "SOME_OP_ID"

        expected = os.path.join(op_server.output_basedir, f"{id}.json")
        assert op_server.get_output_file_path(id) == expected

    @patch("os.path.exists")
    def test__write_file_file_already_exists(self, mock_exists, op_server):
        """Test :meth:`OperationServer._write_file`.

        Ensure an exception is raised if the file path already exists.
        """
        file_path = "/SOME/FILE"
        file_content = {"SOME": "CONTENT"}

        mock_exists.return_value = True

        with pytest.raises(FileExistsError) as exc:
            op_server._write_file(file_path, file_content)

        mock_exists.assert_called_once_with(file_path)

        assert str(str(exc.value)) == f"File '{file_path}' already exists"

    @patch("json.dump")
    @patch("builtins.open")
    @patch("os.path.exists")
    def test__write_file_ok(self, mock_exists, mock_open, mock_dump,
                            op_server):
        """Test :meth:`OperationServer._write_file`.

        Ensure the file is created with the expected content.
        """
        file_path = "/SOME/FILE"
        file_content = {"SOME": "CONTENT"}

        mock_open.return_value.__enter__.return_value = "SOME_FILE_DESCRIPTOR"

        mock_exists.return_value = False

        op_server._write_file(file_path, file_content)
        mock_open.assert_called_once_with(file_path, "w")
        mock_dump.assert_called_once_with(file_content, "SOME_FILE_DESCRIPTOR")

    @pytest.mark.parametrize("content,missing_keys", [
        ({}, "operation_type, start_time",),
        ({"operation_type": "SOME_OPERATION_TYPE"}, "start_time"),
        ({"start_time": "SOME_START_TIME"}, "operation_type",),
    ])
    def test_write_job_file_content_missing_keys(self, content, missing_keys,
                                                 op_server):
        """Test :meth:`OperationServer.write_job_file`.

        Ensure an exception is raised if the content is missing keys.
        """
        id = "SOME_OP_ID"

        with pytest.raises(MalformedContent) as exc:
            op_server.write_job_file(id, content)

        expected = (
            f"Job file for operation '{id}' is missing required "
            f"keys: {missing_keys}"
        )
        assert str(exc.value) == expected

    def test_write_job_file_file_already_exists(self, op_server):
        """Test :meth:`OperationServer.write_job_file`.

        Ensure an exception is raised if the file already exists.
        """
        content = {
            "operation_type": "SOME_OPERATION_TYPE",
            "start_time": "SOME_START_TIME",
        }

        with patch.object(op_server, "_write_file") as mock_write_file:
            mock_write_file.side_effect = FileExistsError

            with pytest.raises(FileExistsError) as exc:
                op_server.write_job_file(id, content)

            expected = f"Job file for operation '{id}' already exists"
            assert str(exc.value) == expected

    def test_write_job_file_ok(self, op_server):
        """Test :meth:`OperationServer.write_job_file`.

        Ensure the file is written if everything is fine.
        """
        content = {
            "operation_type": "SOME_OPERATION_TYPE",
            "start_time": "SOME_START_TIME",
        }

        with patch.object(op_server, "_write_file") as mock_write_file:
            op_server.write_job_file(id, content)

            mock_write_file.assert_called_once_with(
                op_server.get_job_file_path(id),
                content,
            )

    @pytest.mark.parametrize("content,missing_keys", [
        ({}, "end_time, output, success",),
        ({"end_time": "SOME_END_TIME"}, "output, success"),
        ({"output": "SOME_OUTPUT"}, "end_time, success",),
        ({"success": "SOME_SUCCESS"}, "end_time, output",),
        ({"end_time": "SOME_END_TIME", "output": "SOME_OUTPUT"}, "success"),
        ({"end_time": "SOME_END_TIME", "success": "SOME_SUCCESS"}, "output"),
        ({"output": "SOME_OUTPUT", "success": "SOME_SUCCESS"}, "end_time"),
    ])
    def test_write_output_file_content_missing_keys(self, content,
                                                    missing_keys, op_server):
        """Test :meth:`OperationServer.write_output_file`.

        Ensure an exception is raised if the content is missing keys.
        """
        id = "SOME_OP_ID"

        with pytest.raises(MalformedContent) as exc:
            op_server.write_output_file(id, content)

        expected = (
            f"Output file for operation '{id}' is missing required "
            f"keys: {missing_keys}"
        )
        assert str(exc.value) == expected

    def test_write_output_file_file_already_exists(self, op_server):
        """Test :meth:`OperationServer.write_output_file`.

        Ensure an exception is raised if the file already exists.
        """
        content = {
            "end_time": "SOME_END_TIME",
            "output": "SOME_OUTPUT",
            "success": "SOME_SUCCESS",
        }

        with patch.object(op_server, "_write_file") as mock_write_file:
            mock_write_file.side_effect = FileExistsError

            with pytest.raises(FileExistsError) as exc:
                op_server.write_output_file(id, content)

            expected = f"Output file for operation '{id}' already exists"
            assert str(exc.value) == expected

    def test_write_output_file_ok(self, op_server):
        """Test :meth:`OperationServer.write_output_file`.

        Ensure the file is written if everything is fine.
        """
        content = {
            "end_time": "SOME_END_TIME",
            "output": "SOME_OUTPUT",
            "success": "SOME_SUCCESS",
        }

        with patch.object(op_server, "_write_file") as mock_write_file:
            op_server.write_output_file(id, content)

            mock_write_file.assert_called_once_with(
                op_server.get_output_file_path(id),
                content,
            )

    @patch("json.load")
    @patch("builtins.open")
    def test__read_file(self, mock_open, mock_load, op_server):
        """Test :meth:`OperationServer._read_file`.

        Ensure the file is read and its content is parsed from JSON.
        """
        file_path = "/SOME/FILE"

        mock_open.return_value.__enter__.return_value = "SOME_FILE_DESCRIPTOR"

        op_server._read_file(file_path)
        mock_open.assert_called_once_with(file_path)
        mock_load.assert_called_once_with("SOME_FILE_DESCRIPTOR")

    def test_read_job_file_file_does_not_exist(self, op_server):
        """Test :meth:`OperationServer._read_job_file`.

        Ensure an exception is raised if the file does not exist.
        """
        id = "SOME_OP_ID"

        with patch.object(op_server, "_read_file") as mock_read_file:
            mock_read_file.side_effect = FileNotFoundError

            with pytest.raises(FileNotFoundError) as exc:
                op_server.read_job_file(id)

            expected = f"Job file for operation '{id}' does not exist"
            assert str(exc.value) == expected

    def test_read_job_file_ok(self, op_server):
        """Test :meth:`OperationServer._read_job_file`.

        Ensure its content is retrieved if everything is fine.
        """
        id = "SOME_OP_ID"
        content = {
            "operation_type": "SOME_OPERATION_TYPE",
            "start_time": "SOME_START_TIME",
        }

        with patch.object(op_server, "_read_file") as mock_read_file:
            mock_read_file.return_value = content

            assert op_server.read_job_file(id) == content

    def test_read_output_file_file_does_not_exist(self, op_server):
        """Test :meth:`OperationServer._read_output_file`.

        Ensure and exception is raised if the file does not exist.
        """
        id = "SOME_OP_ID"

        with patch.object(op_server, "_read_file") as mock_read_file:
            mock_read_file.side_effect = FileNotFoundError

            with pytest.raises(FileNotFoundError) as exc:
                op_server.read_output_file(id)

            expected = f"Output file for operation '{id}' does not exist"
            str(exc.value) == expected

    def test_read_output_file_ok(self, op_server):
        """Test :meth:`OperationServer._read_output_file`.

        Ensure its content is retrieved if everything is fine.
        """
        id = "SOME_OP_ID"
        content = {
            "success": "SOME_SUCCESS",
            "end_time": "SOME_END_TIME",
            "output": "SOME_OUTPUT",
        }

        with patch.object(op_server, "_read_file") as mock_read_file:
            mock_read_file.return_value = content

            assert op_server.read_output_file(id) == content

    @patch("os.listdir")
    def test_get_operations_list_empty_list(self, mock_listdir, op_server):
        """Test :meth:`OperationServer.get_operations_list`.

        Ensure it returns an empty list if there are no job files.
        """
        mock_listdir.return_value = []

        assert op_server.get_operations_list() == []

        mock_listdir.assert_called_once_with(op_server.jobs_basedir)

    @patch("os.listdir")
    def test_get_operations_list_ignore_non_json_files(self, mock_listdir,
                                                       op_server):
        """Test :meth:`OperationServer.get_operations_list`.

        Ensure non-JSON files are not considered.
        """
        mock_listdir.return_value = [
            "SOME_OPERATION_1.txt",
            "SOME_OPERATION_2.xml",
            "SOME_OPERATION_3.png",
        ]

        assert op_server.get_operations_list() == []

        mock_listdir.assert_called_once_with(op_server.jobs_basedir)

    @patch("pg_backup_api.server_operation.OperationServer.read_job_file")
    @patch("os.listdir")
    def test_get_operations_list_with_no_filters(self, mock_listdir,
                                                 mock_read_job_file,
                                                 op_server):
        """Test :meth:`OperationServer.get_operations_list`.

        Ensure expected operations are returned if no filters are applied.
        """
        mock_listdir.return_value = [
            "SOME_OPERATION_1.json",
            "SOME_OPERATION_2.json",
        ]

        mock_read_job_file.side_effect = [
            {"operation_type": "SOME_OPERATION_TYPE_1"},
            {"operation_type": "SOME_OPERATION_TYPE_2"},
        ]

        expected = [
            {
                "id": "SOME_OPERATION_1",
                "type": "SOME_OPERATION_TYPE_1",
            },
            {
                "id": "SOME_OPERATION_2",
                "type": "SOME_OPERATION_TYPE_2",
            },
        ]
        assert op_server.get_operations_list() == expected

        mock_read_job_file.assert_has_calls([
            call("SOME_OPERATION_1"),
            call("SOME_OPERATION_2"),
        ])

    @patch("pg_backup_api.server_operation.OperationServer.read_job_file")
    @patch("os.listdir")
    def test_get_operations_list_with_filters(self, mock_listdir,
                                              mock_read_job_file, op_server):
        """Test :meth:`OperationServer.get_operations_list`.

        Ensure expected operations are returned if filters are applied.
        """
        mock_listdir.return_value = [
            "SOME_OPERATION_1.json",
            "SOME_OPERATION_2.json",
        ]

        mock_read_job_file.side_effect = [
            {"operation_type": "recovery"},
            {"operation_type": "SOME_OPERATION_TYPE_2"},
        ]

        expected = [
            {
                "id": "SOME_OPERATION_1",
                "type": "recovery",
            },
        ]
        result = op_server.get_operations_list(OperationType.RECOVERY)
        assert result == expected

        mock_read_job_file.assert_has_calls([
            call("SOME_OPERATION_1"),
            call("SOME_OPERATION_2"),
        ])

    @patch("pg_backup_api.server_operation.OperationServer.read_output_file")
    @patch("pg_backup_api.server_operation.OperationServer.read_job_file")
    def test_get_operation_status_done(self, mock_read_job_file,
                                       mock_read_output_file, op_server):
        """Test :meth:`OperationServer.get_operation_status`.

        Ensure it returns ``DONE`` if the output file is successful.
        """
        id = "SOME_OP_ID"

        mock_read_output_file.return_value = {"success": True}

        assert op_server.get_operation_status(id) == "DONE"

        mock_read_job_file.assert_not_called()
        mock_read_output_file.assert_called_once_with(id)

    @patch("pg_backup_api.server_operation.OperationServer.read_output_file")
    @patch("pg_backup_api.server_operation.OperationServer.read_job_file")
    def test_get_operation_status_failed(self, mock_read_job_file,
                                         mock_read_output_file, op_server):
        """Test :meth:`OperationServer.get_operation_status`.

        Ensure it returns ``FAILED`` if the output file is not successful.
        """
        id = "SOME_OP_ID"

        mock_read_output_file.return_value = {"success": False}

        assert op_server.get_operation_status(id) == "FAILED"

        mock_read_job_file.assert_not_called()
        mock_read_output_file.assert_called_once_with(id)

    @patch("pg_backup_api.server_operation.OperationServer.read_output_file")
    @patch("pg_backup_api.server_operation.OperationServer.read_job_file")
    def test_get_operation_status_in_progress(self, mock_read_job_file,
                                              mock_read_output_file,
                                              op_server):
        """Test :meth:`OperationServer.get_operation_status`.

        Ensure it returns ``IN_PROGRESS`` if the job file exists, but no
        output file exists.
        """
        id = "SOME_OP_ID"

        mock_read_job_file.return_value = {}
        mock_read_output_file.side_effect = FileNotFoundError

        assert op_server.get_operation_status(id) == "IN_PROGRESS"

        mock_read_job_file.assert_called_once_with(id)
        mock_read_output_file.assert_called_once_with(id)

    @patch("pg_backup_api.server_operation.OperationServer.read_output_file")
    @patch("pg_backup_api.server_operation.OperationServer.read_job_file")
    def test_get_operation_status_exception(self, mock_read_job_file,
                                            mock_read_output_file,
                                            op_server):
        """Test :meth:`OperationServer.get_operation_status`.

        Ensure an exception is raised if neither job nor output file exist.
        """
        id = "SOME_OP_ID"

        mock_read_job_file.side_effect = FileNotFoundError
        mock_read_output_file.side_effect = FileNotFoundError

        with pytest.raises(OperationNotExists) as exc:
            op_server.get_operation_status(id)

        assert str(exc.value) == f"Operation '{id}' does not exist"

        mock_read_job_file.assert_called_once_with(id)
        mock_read_output_file.assert_called_once_with(id)


@patch("pg_backup_api.server_operation.OperationServer", MagicMock())
class TestOperation:
    """Run tests for :class:`Operation`."""

    @pytest.fixture
    @patch("pg_backup_api.server_operation.OperationServer", MagicMock())
    def operation(self):
        """Create an :class:`Operation` instance for testing.

        :return: a new instance of :class:`Operation` for testing.
        """
        return Operation(_BARMAN_SERVER)

    def test___init___auto_id(self, operation):
        """Test :meth:`Operation.__init__`.

        Ensure the ID is automatically generated, if no custom one is given.
        """
        id = "AUTO_ID"

        with patch.object(Operation, "_generate_id") as mock_generate_id:
            mock_generate_id.return_value = id
            operation = Operation(_BARMAN_SERVER)
            assert operation.id == id
            mock_generate_id.assert_called_once()

    def test___init___custom_id(self, operation):
        """Test :meth:`Operation.__init__`.

        Ensure a custom ID is considered, if a custom one is given.
        """
        id = "CUSTOM_OP_ID"

        with patch.object(Operation, "_generate_id") as mock_generate_id:
            operation = Operation(_BARMAN_SERVER, id)
            assert operation.id == id
            mock_generate_id.assert_not_called()

    def test__generate_id(self, operation):
        """Test :meth:`Operation._generate_id`.

        Ensure it generates an ID based on current timestamp.
        """
        with patch("pg_backup_api.server_operation.datetime") as mock_datetime:
            mock_datetime.now.return_value = MagicMock()
            operation._generate_id()
            mock_datetime.now.return_value.strftime.assert_called_once_with(
                "%Y%m%dT%H%M%S",
            )

    def test_time_even_now(self, operation):
        """Test :meth:`Operation.time_event_now`.

        Ensure the timestamp is generated in the expected format.
        """
        with patch("pg_backup_api.server_operation.datetime") as mock_datetime:
            mock_datetime.now.return_value = MagicMock()
            operation.time_event_now()
            mock_datetime.now.return_value.strftime.assert_called_once_with(
                "%Y-%m-%dT%H:%M:%S.%f",
            )

    def test_job_file(self, operation):
        """Test :meth:`Operation.job_file`.

        Ensure :meth:`OperationServer.get_job_file_path` is called to satisfy
        the property.
        """
        operation.job_file
        operation.server.get_job_file_path.assert_called_once_with(
            operation.id,
        )

    def test_output_file(self, operation):
        """Test :meth:`Operation.output_file`.

        Ensure :meth:`OperationServer.get_output_file_path is called to satisfy
        the property.
        """
        operation.output_file
        operation.server.get_output_file_path.assert_called_once_with(
            operation.id,
        )

    def test_read_job_file(self, operation):
        """Test :meth:`Operation.read_job_file`.

        Ensure :meth:`OperationServer.read_job_file` is called as expected.
        """
        operation.read_job_file()
        operation.server.read_job_file.assert_called_once_with(
            operation.id,
        )

    def test_read_output_file(self, operation):
        """Test :meth:`Operation.read_output_file`.

        Test :meth:`OperationServer.read_output_file` is called as expected.
        """
        operation.read_output_file()
        operation.server.read_output_file.assert_called_once_with(
            operation.id,
        )

    def test_write_job_file(self, operation):
        """Test :meth:`Operation.write_jobf_file`.

        Ensure :meth:`OperationServer.write_job_file` is called as expected.
        """
        content = {"SOME": "CONTENT"}
        operation.write_job_file(content)
        operation.server.write_job_file.assert_called_once_with(
            operation.id,
            content,
        )

    def test_write_output_file(self, operation):
        """Test :meth:`Operation.write_output_file`.

        Ensure :meth:`OperationServer.write_output_file` is called as expected.
        """
        content = {"SOME": "CONTENT"}
        operation.write_output_file(content)
        operation.server.write_output_file.assert_called_once_with(
            operation.id,
            content,
        )

    def test_get_status(self, operation):
        """Test :meth:`Operation.get_status`.

        Test :meth:`OperationServer.get_operation_status` is called as
        expected.
        """
        operation.get_status()
        operation.server.get_operation_status.assert_called_once_with(
            operation.id,
        )

    def test__run_subprocess(self, operation):
        """Test :meth:`Operation._run_subprocess`.

        Ensure it has the expected interactions with :mod:`subprocess`.
        """
        cmd = ["SOME", "COMMAND"]
        stdout = "SOME OUTPUT"
        return_code = 0

        with patch("subprocess.Popen", MagicMock()) as mock_popen:
            mock_popen.return_value.communicate.return_value = (stdout, None)
            mock_popen.return_value.returncode = return_code

            assert operation._run_subprocess(cmd) == (stdout, return_code)

            mock_popen.assert_called_once_with(cmd, stdout=subprocess.PIPE,
                                               stderr=subprocess.STDOUT)

    def test_run(self, operation):
        """Test :meth:`Operation.run`.

        Ensure :meth:`Operation._run_logic` is called.
        """
        with patch.object(operation, "_run_logic") as mock_run_logic:
            operation.run()
            mock_run_logic.assert_called_once()


@patch("pg_backup_api.server_operation.OperationServer", MagicMock())
class TestRecoveryOperation:
    """Run tests for :class:`RecoveryOperation`."""

    @pytest.fixture
    @patch("pg_backup_api.server_operation.OperationServer", MagicMock())
    def operation(self):
        """Create a :class:`RecoveryOperation` instance for testing.

        :return: a new instance of :class:`RecoveryOperation` for testing.
        """
        return RecoveryOperation(_BARMAN_SERVER)

    @pytest.mark.parametrize("content,missing_keys", [
        ({}, "backup_id, destination_directory, remote_ssh_command",),
        ({"backup_id": "SOME_BACKUP_ID"},
         "destination_directory, remote_ssh_command"),
        ({"destination_directory": "SOME_DESTINATION_DIRECTORY"},
         "backup_id, remote_ssh_command",),
        ({"remote_ssh_command": "SOME_REMOTE_SSH_COMMAND"},
         "backup_id, destination_directory",),
        ({"backup_id": "SOME_BACKUP_ID",
          "destination_directory": "SOME_DESTINATION_DIRECTORY"},
         "remote_ssh_command"),
        ({"backup_id": "SOME_BACKUP_ID",
          "remote_ssh_command": "SOME_REMOTE_SSH_COMMAND"},
         "destination_directory"),
        ({"destination_directory": "SOME_DESTINATION_DIRECTORY",
          "remote_ssh_command": "SOME_REMOTE_SSH_COMMAND"},
         "backup_id"),
    ])
    def test__validate_job_content_content_missing_keys(self, content,
                                                        missing_keys,
                                                        operation):
        """Test :meth:`RecoveryOperation._validate_job_content`.

        Ensure and exception is raised if the content is missing keys.
        """
        with pytest.raises(MalformedContent) as exc:
            operation._validate_job_content(content)

        assert str(exc.value) == f"Missing required arguments: {missing_keys}"

    def test__validate_job_content_ok(self, operation):
        """Test :meth:`RecoveryOperation._validate_job_content`.

        Ensure execution is fine if everything is filled as expected.
        """
        content = {
            "backup_id": "SOME_BACKUP_ID",
            "destination_directory": "SOME_DESTINATION_DIRECTORY",
            "remote_ssh_command": "SOME_REMOTE_SSH_COMMAND",
        }
        operation._validate_job_content(content)

    @patch("pg_backup_api.server_operation.Operation.time_event_now")
    @patch("pg_backup_api.server_operation.Operation.write_job_file")
    def test_write_job_file(self, mock_write_job_file, mock_time_event_now,
                            operation):
        """Test :meth:`RecoveryOperation.write_job_file`.

        Ensure the underlying methods are called as expected.
        """
        content = {
            "SOME": "CONTENT",
        }
        extended_content = {
            "SOME": "CONTENT",
            "operation_type": OperationType.RECOVERY.value,
            "start_time": "SOME_TIMESTAMP",
        }

        with patch.object(operation, "_validate_job_content") as mock:
            mock_time_event_now.return_value = "SOME_TIMESTAMP"

            operation.write_job_file(content)

            mock_time_event_now.assert_called_once()
            mock.assert_called_once_with(extended_content)
            mock_write_job_file.assert_called_once_with(extended_content)

    def test__get_args(self, operation):
        """Test :meth:`RecoveryOperation._get_args`.

        Ensure it returns the correct arguments for ``barman recover``.
        """
        with patch.object(operation, "read_job_file") as mock:
            mock.return_value = {
                "backup_id": "SOME_BACKUP_ID",
                "destination_directory": "SOME_DESTINATION_DIRECTORY",
                "remote_ssh_command": "SOME_REMOTE_SSH_COMMAND",
            }

            expected = [
                operation.server.name,
                "SOME_BACKUP_ID",
                "SOME_DESTINATION_DIRECTORY",
                "--remote-ssh-command",
                "SOME_REMOTE_SSH_COMMAND",
            ]
            assert operation._get_args() == expected

    @patch("pg_backup_api.server_operation.Operation._run_subprocess")
    @patch("pg_backup_api.server_operation.RecoveryOperation._get_args")
    def test__run_logic(self, mock_get_args, mock_run_subprocess, operation):
        """Test :meth:`RecoveryOperation._run_logic`.

        Ensure the underlying calls occur as expected.
        """
        arguments = ["SOME", "ARGUMENTS"]
        output = ("SOME OUTPUT", 0)

        mock_get_args.return_value = arguments
        mock_run_subprocess.return_value = output

        assert operation._run_logic() == output

        mock_get_args.assert_called_once()
        mock_run_subprocess.assert_called_once_with(
            ["barman", "recover"] + arguments,
        )
