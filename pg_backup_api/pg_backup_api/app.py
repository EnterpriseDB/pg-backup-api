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

"""
Used when running pg-backup-api REST API server as an WSGI application.

Load Barman configuration, set up logging for WSGI, and set up a JSON console
output writer.

.. note::
    This is designed for production usage, while the ``pg-backup-api serve``
    command is designed for development usage.

:var application: the Flask application instance.
"""
from barman import output

from pg_backup_api.run import app
from pg_backup_api.utils import (
    load_barman_config,
    setup_logging_for_wsgi_server
)

load_barman_config()
setup_logging_for_wsgi_server()
output.set_output_writer(output.AVAILABLE_WRITERS["json"]())
application = app
