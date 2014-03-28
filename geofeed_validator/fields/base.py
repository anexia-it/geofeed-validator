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

import netaddr
import pycountry
import six


class Field(object):
    '''
    Base class for representing a field
    '''
    ERROR = None
    WARNING = None
    NAME = None

    def __init__(self):
        if not isinstance(getattr(self, 'ERROR', None), six.string_types):
            raise ValueError('ERROR class-attribute of %r not set or invalid.' % self.__class__)
        if not isinstance(getattr(self, 'NAME', None), six.string_types):
            raise ValueError('NAME class-attribute of %r not set or invalid.' % self.__class__)
        self._name = self.NAME

    @property
    def name(self):
        return self._name

    def _check_errors(self, value):
        raise NotImplementedError

    def _check_warnings(self, value):
        return False

    def validate(self, value):
        errors = self._normalize_check_result(self._check_errors(value), self.ERROR)
        warnings = self._normalize_check_result(self._check_warnings(value), self.WARNING)

        cleaned_value = None
        try:
            cleaned_value = self.to_python(value)
        except:
            pass

        return errors, warnings, cleaned_value

    @staticmethod
    def _normalize_check_result(check_result, default):
        if check_result is None:
            raise ValueError('None is not an allowed value.')

        if check_result is False:
            return tuple()

        if check_result is True and default:
            check_result = (default,)

        if isinstance(check_result, six.string_types):
            check_result = (check_result,)

        if not type(check_result) in (list, tuple):
            raise ValueError('Error lists must be of type list or tuple.')

        if len(filter(lambda s: isinstance(s, six.string_types), check_result)) != len(check_result):
            raise ValueError('At least one non-string error was returned.')

        return check_result

    def to_python(self, value):
        raise NotImplementedError

    def to_string(self, value):
        try:
            return str(self.to_python(value))
        except Exception:
            pass
        return None


    def __repr__(self):
        return '<Field %s>' % (self.name)


class NetworkField(Field):
    ERROR = 'Not a valid IP network'
    ERROR_LOOPBACK = 'Loopback network not allowed'
    ERROR_PRIVATE = 'Private network not allowed'
    ERROR_RESERVED = 'Reserved network not allowed'
    ERROR_MULTICAST = 'Multicast network not allowed'
    NAME = 'network'

    def _check_errors(self, value):
        net = None
        try:
            net = self.to_python(value)
        except:
            return True

        if net.is_loopback():
            return self.ERROR_LOOPBACK
        elif net.is_private():
            return self.ERROR_PRIVATE
        elif net.is_reserved():
            return self.ERROR_RESERVED
        elif net.is_multicast():
            return self.ERROR_MULTICAST

        return False

    def to_python(self, value):
        return netaddr.IPNetwork(value)


class CountryField(Field):
    ERROR = 'Not a valid ISO3316-2 country code'
    NAME = 'country'

    def _check_errors(self, value):
        try:
            self.to_python(value)
        except:
            return True
        return False

    def to_python(self, value):
        if value:
            return pycountry.countries.get(alpha2=value)
        return None

    def to_string(self, value):
        if value:
            try:
                country = self.to_python(value)
                return country.alpha2
            except:
                pass
        return ''


class SubdivisionField(Field):
    ERROR = 'Not a valid ISO3316-2 subdivision code'
    NAME = 'subdivision'

    def _check_errors(self, value):
        try:
            self.to_python(value)
        except:
            return True
        return False

    def to_python(self, value):
        if value:
            return pycountry.subdivisions.get(code=value)
        return None

    def to_string(self, value):
        if value:
            try:
                subdivision = self.to_python(value)
                return subdivision.code
            except:
                pass
        return ''


class CityField(Field):
    ERROR = 'unvalidated'
    NAME = 'city'

    def _check_errors(self, value):
        # TODO: city is not validated right now
        return False

    def to_python(self, value):
        return value


class ZipCodeField(Field):
    ERROR = 'unvalidated'
    NAME = 'zipcode'

    def _check_errors(self, value):
        # TODO: zip code is not validated right now
        return False

    def to_python(self, value):
        return value