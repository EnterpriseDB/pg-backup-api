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

# This file was autogenerated by OpenAPI Generator.

# flake8: noqa
from __future__ import absolute_import

# import models into model package
from pg_backup_api.openapi_server.models.config import Config
from pg_backup_api.openapi_server.models.copy_stats import CopyStats
from pg_backup_api.openapi_server.models.copy_stats_analysis_time_per_item import (
    CopyStatsAnalysisTimePerItem,
)
from pg_backup_api.openapi_server.models.copy_stats_copy_time_per_item import (
    CopyStatsCopyTimePerItem,
)
from pg_backup_api.openapi_server.models.copy_stats_serialized_copy_time_per_item import (
    CopyStatsSerializedCopyTimePerItem,
)
from pg_backup_api.openapi_server.models.diagnose_output import DiagnoseOutput
from pg_backup_api.openapi_server.models.diagnose_output_global import (
    DiagnoseOutputGlobal,
)
from pg_backup_api.openapi_server.models.diagnose_output_servers import (
    DiagnoseOutputServers,
)
from pg_backup_api.openapi_server.models.global_config import GlobalConfig
from pg_backup_api.openapi_server.models.last_archived_wal import LastArchivedWal
from pg_backup_api.openapi_server.models.server_config import ServerConfig
from pg_backup_api.openapi_server.models.status import Status
from pg_backup_api.openapi_server.models.system_info import SystemInfo
from pg_backup_api.openapi_server.models.wals import Wals
