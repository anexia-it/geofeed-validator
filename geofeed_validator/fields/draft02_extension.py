# geofeed_validator/fields/base.py
#
# ANEXIA GeoFeed Validator
#
# Copyright (C) 2014 ANEXIA Internetdienstleistungs GmbH
#
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#
# Stephan Peijnik <speijnik@anexia-it.com>
#

from geofeed_validator.fields import Field


class AllocationSizeField(Field):
    ERROR = 'Must be valid CIDR notation'
    NAME = 'allocation_size'

    def _check_errors(self, value):
        try:
            self.to_python(value)
        except Exception as e:
            return True
        return False

    def to_python(self, value):
        if value and not value.startswith('/'):
            raise ValueError('Value does not start with a slash')
        elif value:
            return int(value[1:])
        else:
            return ''
