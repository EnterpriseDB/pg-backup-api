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

import sys

if sys.version_info < (3, 7):
    import typing

    def is_generic(klass):
        """Determine whether klass is a generic class"""
        return type(klass) == typing.GenericMeta

    def is_dict(klass):
        """Determine whether klass is a Dict"""
        return klass.__extra__ == dict

    def is_list(klass):
        """Determine whether klass is a List"""
        return klass.__extra__ == list

else:

    def is_generic(klass):
        """Determine whether klass is a generic class"""
        return hasattr(klass, "__origin__")

    def is_dict(klass):
        """Determine whether klass is a Dict"""
        return klass.__origin__ == dict

    def is_list(klass):
        """Determine whether klass is a List"""
        return klass.__origin__ == list
