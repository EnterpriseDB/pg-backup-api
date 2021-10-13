# -*- coding: utf-8 -*-
# © Copyright EnterpriseDB UK Limited 2013-2021
#
# This file is part of Barman.
#
# Barman is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Barman is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Barman.  If not, see <http://www.gnu.org/licenses/>.

import connexion
import six

from openapi_server.models.diagnose_output import DiagnoseOutput  # noqa: E501
from logic.controller import Controller
from pg_backup_api.openapi_server import util


def diagnose():  # noqa: E501
    """Return barman diagnose information

     # noqa: E501


    :rtype: DiagnoseOutput
    """
    return Controller.call_method("diagnose", 
                                  )


def status():  # noqa: E501
    """Check if Barman API App running

     # noqa: E501


    :rtype: str
    """
    return Controller.call_method("status", 
                                  )
