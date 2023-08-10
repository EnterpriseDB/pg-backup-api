import argparse
import json
import logging
import os
import sys

from datetime import datetime
from os.path import join

from pg_backup_api.utils import barman, load_barman_config, get_server_by_name

load_barman_config()

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger()


DEFAULT_OP_TYPE = "recovery"
JOBS_DIR = "jobs"
OUTPUT_DIR = "output"
REQUIRED_OPTIONS = ("backup_id", "destination_directory", "remote_ssh_command")


class Metadata(object):
    def __init__(self, server_name, operation_id=None):
        self.operation_type = DEFAULT_OP_TYPE
        self.operation_id = operation_id
        self.server_name = server_name
        self.server_config = get_server_by_name(server_name)
        if not self.server_config:
            raise ServerOperationConfigError(
                f"No barman config found for '{server_name}'."
            )

        barman_home = barman.__config__.barman_home
        self.jobs_basedir = join(barman_home, server_name, JOBS_DIR)
        self.output_basedir = join(barman_home, server_name, OUTPUT_DIR)


class ServerOperation(Metadata):
    def get_operations_list(self):
        jobs_list = []
        jobs_basedir = self.jobs_basedir
        if os.path.exists(jobs_basedir):
            for job in [files for _, _, files in os.walk(jobs_basedir)][0]:
                if job.endswith(".json"):
                    operation_id, _ = job.split(".json")
                    jobs_list.append(operation_id)
        return jobs_list

    def get_status_by_operation_id(self):
        output_file = self.get_output_file()
        if not os.path.exists(output_file):
            if os.path.exists(self.get_job_file()):
                return "IN_PROGRESS"
            else:
                raise Exception("Invalid operation-id")

        with open(self.get_output_file()) as file_object:
            content = json.load(file_object)
            return "DONE" if content.get("success") else "FAILED"

    @staticmethod
    def time_event_now():
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

    def copy_and_validate_options(self, general_options):
        job_data = {
            "operation_type": self.operation_type,
            "start_time": ServerOperation.time_event_now(),
        }
        for required_key in REQUIRED_OPTIONS:
            job_data[required_key] = general_options[required_key]

        return job_data

    def create_job_file(self, general_options):
        if not os.path.exists(self.jobs_basedir):
            os.makedirs(self.jobs_basedir)

        job_data = self.copy_and_validate_options(general_options)
        self.__create_file(self.jobs_basedir, job_data)

    def create_output_file(self, content_file):
        if not os.path.exists(self.output_basedir):
            os.makedirs(self.output_basedir)

        self.__create_file(self.output_basedir, content_file)

    def __create_file(self, file_type, content):
        if not self.operation_id:
            raise Exception("operation_id is required here")

        file_name = f"{self.operation_id}.json"
        fpath = join(file_type, file_name)
        if os.path.exists(fpath):
            raise Exception("duplicated operation-id")

        with open(fpath, "w") as written_file:
            json.dump(content, written_file)

    def get_job_file_content(self):
        with open(self.get_job_file()) as file_object:
            return json.load(file_object)

    def get_output_file(self):
        return self.__files_path(self.output_basedir)

    def get_job_file(self):
        return self.__files_path(self.jobs_basedir)

    def __files_path(self, basedir):
        if not os.path.exists(basedir):
            msg = f"Couldn't find a task for server '{self.server_name}'"
            raise Exception(msg)

        if not self.operation_id:
            raise Exception("operation_id is required here")

        file_name = f"{self.operation_id}.json"
        fpath = join(basedir, file_name)
        return fpath


class ServerOperationConfigError(ValueError):
    pass


def main(callback):

    try:
        log.info(callback())
    except Exception as e:
        # TODO: we might behave differently depending upon the type here
        log.error(e)
        return -1

    return 0


if __name__ == "__main__":

    operations_commands = {
        "list-operations": "get_operations_list",
        "create-operation": "create_job_file",
        "get-operation": "get_status_by_operation_id",
    }
    parser = argparse.ArgumentParser(
        description="Alternative to the REST API, so one can list, create and "
                    "get information about jobs without a running REST API.",
    )
    parser.add_argument(
        "--server-name", required=True,
        help="Name of the Barman server related to the recovery "
             "operation.",
    )
    parser.add_argument(
        "--operation-id",
        help="ID of the recovery operation, if you are trying to query an "
             "existing operation."
    )
    parser.add_argument(
        "command",
        choices=operations_commands.keys(),
        help="What we should do -- list recovery operations, create a new "
             "recovery operation, or get info about a specific recovery "
             "operation.",
    )

    args = parser.parse_args()
    op = ServerOperation(args.server_name, args.operation_id)
    callback = getattr(op, operations_commands[args.command])

    retval = main(callback)
    sys.exit(retval)
