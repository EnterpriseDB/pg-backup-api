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

import json
import shutil
import subprocess

from pg_backup_api.openapi_server.util import deserialize_model
from pg_backup_api.openapi_server.models.diagnose_output import DiagnoseOutput

# Allow 10 minutes for the barman diagnose command to complete
DIAGNOSE_CMD_TIMEOUT = 600


class UtilityController:
    def diagnose(self):
        # new outputs are appended, so grab the last one
        barman_path = shutil.which("barman")
        with subprocess.Popen(
            [barman_path, "diagnose"], stderr=subprocess.PIPE, stdout=subprocess.PIPE
        ) as p:
            try:
                # `barman diagnose` can be quite chatty on stderr but currently we just
                # return the diagnose output so stderr goes nowhere
                out, _err = p.communicate(timeout=DIAGNOSE_CMD_TIMEOUT)
                stored_output = json.loads(out)
                diag_output = deserialize_model(stored_output, DiagnoseOutput)
                return diag_output
            except subprocess.TimeoutExpired:
                p.kill()
                raise

    def status(self):
        return "OK"  # If this app isn't running, we obviously won't return!
