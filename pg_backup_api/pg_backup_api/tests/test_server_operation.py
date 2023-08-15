import os
import subprocess
from unittest import TestCase
from unittest.mock import Mock, MagicMock, call, patch

from pg_backup_api.server_operation import (
    OperationServer,
    MalformedContent,
    OperationType,
    OperationNotExists,
    Operation,
)


_BARMAN_HOME = "/BARMAN/HOME"
_BARMAN_SERVER = "BARMAR_SERVER"


@patch("pg_backup_api.server_operation.get_server_by_name", Mock())
@patch("barman.__config__.barman_home", _BARMAN_HOME)
class TestOperationServer(TestCase):
    
    @patch("pg_backup_api.server_operation.get_server_by_name", Mock())
    @patch("barman.__config__.barman_home", _BARMAN_HOME)
    def setUp(self):
        with patch.object(OperationServer, "_create_dir"):
            self.server = OperationServer(_BARMAN_SERVER)

    def test___init__(self):
        # Ensure name is as expected.
        self.assertEqual(self.server.name, _BARMAN_SERVER)

        # Ensure "jobs" directory is created in expected path.
        self.assertEqual(
            self.server.jobs_basedir,
            os.path.join(_BARMAN_HOME, _BARMAN_SERVER, "jobs"),
        )

        # Ensure "output" directory is created in the expected path.
        self.assertEqual(
            self.server.output_basedir,
            os.path.join(_BARMAN_HOME, _BARMAN_SERVER, "output"),
        )

    @patch("os.makedirs")
    @patch("os.path.isdir")
    @patch("os.path.exists")
    def test__create_dir(self, mock_exists, mock_isdir, mock_makedirs):
        dir_path = "/SOME/DIR"

        # Ensure an exception is raised if path already exists as a file.
        mock_exists.return_value = True
        mock_isdir.return_value = False

        with self.assertRaises(NotADirectoryError) as exc:
            self.server._create_dir(dir_path)

        mock_exists.assert_called_once_with(dir_path)
        mock_isdir.assert_called_once_with(dir_path)

        self.assertEqual(
            str(exc.exception),
            f"'{dir_path}' exists but it is not a directory",
        )

        # Ensure no exception occurs if directory already exists.
        mock_exists.reset_mock()
        mock_isdir.reset_mock()

        mock_exists.return_value = True
        mock_isdir.return_value = True

        self.server._create_dir(dir_path)

        mock_exists.assert_called_once_with(dir_path)
        mock_isdir.assert_called_once_with(dir_path)

        # Ensure directory is created if missing.
        mock_exists.reset_mock()
        mock_isdir.reset_mock()

        mock_exists.return_value = False

        self.server._create_dir(dir_path)

        mock_exists.assert_called_once_with(dir_path)
        mock_isdir.assert_not_called()
        mock_makedirs.assert_called_once_with(dir_path)

    def test__create_jobs_dir(self):
        # Ensure "_create_dir" is called.
        with patch.object(self.server, "_create_dir") as mock:
            self.server._create_jobs_dir()
            mock.assert_called_once_with(self.server.jobs_basedir)
    
    def test__create_output_dir(self):
        # Ensure "_create_dir" is called.
        with patch.object(self.server, "_create_dir") as mock:
            self.server._create_output_dir()
            mock.assert_called_once_with(self.server.output_basedir)

    def test_get_job_file_path(self):
        # Ensure returns expected file path.
        id = "SOME_OP_ID"

        self.assertEqual(
            self.server.get_job_file_path(id),
            os.path.join(self.server.jobs_basedir, f"{id}.json")
        )
    
    def test_get_output_file_path(self):
        # Ensure returns expected file path.
        id = "SOME_OP_ID"

        self.assertEqual(
            self.server.get_output_file_path(id),
            os.path.join(self.server.output_basedir, f"{id}.json")
        )
    
    @patch("json.dump")
    @patch("builtins.open")
    @patch("os.path.exists")
    def test__write_file(self, mock_exists, mock_open, mock_dump):
        file_path = "/SOME/FILE"
        file_content = {"SOME": "CONTENT"}

        # Ensure exception is raised if file path already exists.
        mock_exists.return_value = True

        with self.assertRaises(FileExistsError) as exc:
            self.server._write_file(file_path, file_content)

        mock_exists.assert_called_once_with(file_path)

        self.assertEqual(
            str(exc.exception),
            f"File '{file_path}' already exists",
        )

        # Ensure file is created with expected content.
        mock_exists.reset_mock()
        mock_open.return_value.__enter__.return_value = "SOME_FILE_DESCRIPTOR"

        mock_exists.return_value = False

        self.server._write_file(file_path, file_content)
        mock_open.assert_called_once_with(file_path, "w")
        mock_dump.assert_called_once_with(file_content, "SOME_FILE_DESCRIPTOR")

    def test_write_job_file(self):
        id = "SOME_OP_ID"
        content = {}

        # Ensure exception is raised if content is missing keys -- test 1
        with self.assertRaises(MalformedContent) as exc:
            self.server.write_job_file(id, content)

        self.assertEqual(
            str(exc.exception),
            f"Job file for operation '{id}' is missing required "
            f"keys: operation_type, start_time",
        )

        # Ensure exception is raised if content is missing keys -- test 2
        content["operation_type"] = "SOME_OPERATION_TYPE"

        with self.assertRaises(MalformedContent) as exc:
            self.server.write_job_file(id, content)

        self.assertEqual(
            str(exc.exception),
            f"Job file for operation '{id}' is missing required "
            f"keys: start_time",
        )

        # Ensure exception is raised if file already exists
        content["start_time"] = "SOME_START_TIME"

        with patch.object(self.server, "_write_file") as mock:
            mock.side_effect = FileExistsError
            
            with self.assertRaises(FileExistsError) as exc:
                self.server.write_job_file(id, content)

            self.assertEqual(
                str(exc.exception),
                f"Job file for operation '{id}' already exists",
            )

        # Ensure file is written if everything is fine
        with patch.object(self.server, "_write_file") as mock:
            self.server.write_job_file(id, content)

            mock.assert_called_once_with(
                self.server.get_job_file_path(id),
                content,
            )

    def test_write_output_file(self):
        id = "SOME_OP_ID"
        content = {}

        # Ensure exception is raised if content is missing keys -- test 1
        with self.assertRaises(MalformedContent) as exc:
            self.server.write_output_file(id, content)

        self.assertEqual(
            str(exc.exception),
            f"Output file for operation '{id}' is missing required "
            f"keys: end_time, output, success",
        )

        # Ensure exception is raised if content is missing keys -- test 2
        content["end_time"] = "SOME_END_TIME"

        with self.assertRaises(MalformedContent) as exc:
            self.server.write_output_file(id, content)

        self.assertEqual(
            str(exc.exception),
            f"Output file for operation '{id}' is missing required "
            f"keys: output, success",
        )

        # Ensure exception is raised if content is missing keys -- test 3
        content["output"] = "SOME_OUTPUT"

        with self.assertRaises(MalformedContent) as exc:
            self.server.write_output_file(id, content)

        self.assertEqual(
            str(exc.exception),
            f"Output file for operation '{id}' is missing required "
            f"keys: success",
        )

        # Ensure exception is raised if file already exists
        content["success"] = "SOME_SUCCESS"

        with patch.object(self.server, "_write_file") as mock:
            mock.side_effect = FileExistsError
            
            with self.assertRaises(FileExistsError) as exc:
                self.server.write_output_file(id, content)

            self.assertEqual(
                str(exc.exception),
                f"Output file for operation '{id}' already exists",
            )

        # Ensure file is written if everything is fine
        with patch.object(self.server, "_write_file") as mock:
            self.server.write_output_file(id, content)

            mock.assert_called_once_with(
                self.server.get_output_file_path(id),
                content,
            )

    @patch("json.load")
    @patch("builtins.open")
    def test__read_file(self, mock_open, mock_load):
        file_path = "/SOME/FILE"
        # Ensure file is created with expected content.
        mock_open.return_value.__enter__.return_value = "SOME_FILE_DESCRIPTOR"

        self.server._read_file(file_path)
        mock_open.assert_called_once_with(file_path)
        mock_load.assert_called_once_with("SOME_FILE_DESCRIPTOR")

    def test_read_job_file(self):
        id = "SOME_OP_ID"
        content = {
            "operation_type": "SOME_OPERATION_TYPE",
            "start_time": "SOME_START_TIME",
        }

        # Ensure exception is raised if file does not exist.
        with patch.object(self.server, "_read_file") as mock:
            mock.side_effect = FileNotFoundError
            
            with self.assertRaises(FileNotFoundError) as exc:
                self.server.read_job_file(id)

            self.assertEqual(
                str(exc.exception),
                f"Job file for operation '{id}' does not exist",
            )

        # Ensure content is retrieved if everything is fine.
        with patch.object(self.server, "_read_file") as mock:
            mock.return_value = content

            self.assertEqual(
                self.server.read_job_file(id),
                content,
            )

    def test_read_output_file(self):
        id = "SOME_OP_ID"
        content = {
            "success": "SOME_SUCCESS",
            "end_time": "SOME_END_TIME",
            "output": "SOME_OUTPUT",
        }

        # Ensure exception is raised if file does not exist.
        with patch.object(self.server, "_read_file") as mock:
            mock.side_effect = FileNotFoundError
            
            with self.assertRaises(FileNotFoundError) as exc:
                self.server.read_output_file(id)

            self.assertEqual(
                str(exc.exception),
                f"Output file for operation '{id}' does not exist",
            )

        # Ensure content is retrieved if everything is fine.
        with patch.object(self.server, "_read_file") as mock:
            mock.return_value = content

            self.assertEqual(
                self.server.read_output_file(id),
                content,
            )

    @patch("pg_backup_api.server_operation.OperationServer.read_job_file")
    @patch("os.listdir")
    def test_get_operations_list(self, mock_listdir, mock_read_job_file):
        # Ensure it returns an empty list if there are no job files.
        mock_listdir.return_value = []

        self.assertEqual(
            self.server.get_operations_list(),
            [],
        )

        mock_listdir.assert_called_once_with(self.server.jobs_basedir)

        # Ensure non-JSON files are not considered.
        mock_listdir.reset_mock()

        mock_listdir.return_value = [
            "SOME_OPERATION_1.txt",
            "SOME_OPERATION_2.xml",
            "SOME_OPERATION_3.png",
        ]

        self.assertEqual(
            self.server.get_operations_list(),
            [],
        )

        mock_listdir.assert_called_once_with(self.server.jobs_basedir)

        # Ensure expected operations are returned if no filters.
        mock_listdir.reset_mock()

        mock_listdir.return_value = [
            "SOME_OPERATION_1.json",
            "SOME_OPERATION_2.json",
        ]

        mock_read_job_file.side_effect = [
            {"operation_type": "SOME_OPERATION_TYPE_1"},
            {"operation_type": "SOME_OPERATION_TYPE_2"},
        ]

        self.assertEqual(
            self.server.get_operations_list(),
            [
                {
                    "id": "SOME_OPERATION_1",
                    "type": "SOME_OPERATION_TYPE_1",
                },
                {
                    "id": "SOME_OPERATION_2",
                    "type": "SOME_OPERATION_TYPE_2",
                },
            ],
        )

        mock_read_job_file.assert_has_calls([
            call("SOME_OPERATION_1"),
            call("SOME_OPERATION_2"),
        ])

        # Ensure expected operations are returned if filtering.
        mock_listdir.reset_mock()
        mock_read_job_file.reset_mock()

        mock_listdir.return_value = [
            "SOME_OPERATION_1.json",
            "SOME_OPERATION_2.json",
        ]

        mock_read_job_file.side_effect = [
            {"operation_type": "recovery"},
            {"operation_type": "SOME_OPERATION_TYPE_2"},
        ]

        self.assertEqual(
            self.server.get_operations_list(OperationType.RECOVERY),
            [
                {
                    "id": "SOME_OPERATION_1",
                    "type": "recovery",
                },
            ],
        )

        mock_read_job_file.assert_has_calls([
            call("SOME_OPERATION_1"),
            call("SOME_OPERATION_2"),
        ])

    @patch("pg_backup_api.server_operation.OperationServer.read_output_file")
    @patch("pg_backup_api.server_operation.OperationServer.read_job_file")
    def test_get_operation_status(self, mock_read_job_file,
                                  mock_read_output_file):
        id = "SOME_OP_ID"

        # Ensure returns DONE if output file is successful.
        mock_read_output_file.return_value = {"success": True}

        self.assertEqual(
            self.server.get_operation_status(id),
            "DONE",
        )

        mock_read_job_file.assert_not_called()
        mock_read_output_file.assert_called_once_with(id)

        # Ensure returns FAILED if output file is not successful.
        mock_read_job_file.reset_mock()
        mock_read_output_file.reset_mock()

        mock_read_output_file.return_value = {"success": False}

        self.assertEqual(
            self.server.get_operation_status(id),
            "FAILED",
        )

        mock_read_job_file.assert_not_called()
        mock_read_output_file.assert_called_once_with(id)

        # Ensure returns IN_PROGRESS if job file exists.
        mock_read_job_file.reset_mock()
        mock_read_output_file.reset_mock()

        mock_read_job_file.return_value = {}
        mock_read_output_file.side_effect = FileNotFoundError

        self.assertEqual(
            self.server.get_operation_status(id),
            "IN_PROGRESS",
        )

        mock_read_job_file.assert_called_once_with(id)
        mock_read_output_file.assert_called_once_with(id)

        # Ensure exception is raised if neither job nor output file exists.
        mock_read_job_file.reset_mock()
        mock_read_output_file.reset_mock()

        mock_read_job_file.side_effect = FileNotFoundError
        mock_read_output_file.side_effect = FileNotFoundError

        with self.assertRaises(OperationNotExists) as exc:
            self.server.get_operation_status(id)
        

        self.assertEqual(
            str(exc.exception),
            f"Operation '{id}' does not exist"
        )

        mock_read_job_file.assert_called_once_with(id)
        mock_read_output_file.assert_called_once_with(id)


@patch("pg_backup_api.server_operation.OperationServer", MagicMock())
class TestOperation(TestCase):

    @patch("pg_backup_api.server_operation.OperationServer", MagicMock())
    def setUp(self):
        self.operation = Operation(_BARMAN_SERVER)

    def test___init__(self):
        # Ensure ID is automatically generated, if no custom one is given.
        id = "AUTO_ID"

        with patch.object(Operation, "_generate_id") as mock:
            mock.return_value = id
            operation = Operation(_BARMAN_SERVER)
            self.assertEqual(operation.id, id)
            mock.assert_called_once()

        # Ensure custom ID is considered, if a custom one is given.
        id = "CUSTOM_OP_ID"

        with patch.object(Operation, "_generate_id") as mock:
            operation = Operation(_BARMAN_SERVER, id)
            self.assertEqual(operation.id, id)
            mock.assert_not_called()

    def test__generate_id(self):
        # Ensure generates ID based on current timestamp.
        with patch("pg_backup_api.server_operation.datetime") as mock:
            mock.now.return_value = MagicMock()
            self.operation._generate_id()
            mock.now.return_value.strftime.assert_called_once_with(
                "%Y%m%dT%H%M%S",
            )

    def test_time_even_now(self):
        # Ensure timestamp is generated in the expected format.
        with patch("pg_backup_api.server_operation.datetime") as mock:
            mock.now.return_value = MagicMock()
            self.operation.time_event_now()
            mock.now.return_value.strftime.assert_called_once_with(
                "%Y-%m-%dT%H:%M:%S.%f",
            )

    def test_job_file(self):
        # Ensure get_job_file_path is called to satisfy job_file propety.
        self.operation.job_file
        self.operation.server.get_job_file_path.assert_called_once_with(
            self.operation.id,
        )

    def test_output_file(self):
        # Ensure get_output_file_path is called to satisfy output_file propety.
        self.operation.output_file
        self.operation.server.get_output_file_path.assert_called_once_with(
            self.operation.id,
        )

    def test_read_job_file(self):
        # Ensure OperationServer.read_job_file is called as expected.
        self.operation.read_job_file()
        self.operation.server.read_job_file.assert_called_once_with(
            self.operation.id,
        )
    
    def test_read_output_file(self):
        # Ensure OperationServer.read_output_file is called as expected.
        self.operation.read_output_file()
        self.operation.server.read_output_file.assert_called_once_with(
            self.operation.id,
        )
    
    def test_write_job_file(self):
        # Ensure OperationServer.write_job_file is called as expected.
        content = {"SOME": "CONTENT"}
        self.operation.write_job_file(content)
        self.operation.server.write_job_file.assert_called_once_with(
            self.operation.id,
            content,
        )
    
    def test_write_output_file(self):
        # Ensure OperationServer.write_output_file is called as expected.
        content = {"SOME": "CONTENT"}
        self.operation.write_output_file(content)
        self.operation.server.write_output_file.assert_called_once_with(
            self.operation.id,
            content,
        )
    
    def test_get_status(self):
        # Ensure OperationServer.get_operation_status is called as expected.
        self.operation.get_status()
        self.operation.server.get_operation_status.assert_called_once_with(
            self.operation.id,
        )

    def test__run_subprocess(self):
        # Ensure expected interactions with subprocess module.
        cmd = ["SOME", "COMMAND"]
        stdout = "SOME OUTPUT"
        return_code = 0

        with patch("subprocess.Popen", MagicMock()) as mock:
            mock.return_value.communicate.return_value = (stdout, None)
            mock.return_value.returncode = return_code

            self.assertEqual(
                self.operation._run_subprocess(cmd),
                (stdout, return_code),
            )

            mock.assert_called_once_with(cmd, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)

    def test_run(self):
        # Ensure _run_logic is called.
        with patch.object(self.operation, "_run_logic") as mock:
            self.operation.run()
            mock.assert_called_once()
