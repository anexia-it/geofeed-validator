# geofeed_validator/util.py
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


def is_file_like_object(obj):
    '''
    Helper function that checks if a given object is a file-like object.

    :param obj: Object to check
    :type obj: object
    :returns: True if obj is file-like, False otherwise
    :rtype: bool
    '''
    return hasattr(obj, 'read') and hasattr(obj, 'close')
