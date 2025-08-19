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

from contextlib import suppress

import netaddr
import pycountry


class Field:
    """
    Base class for representing a field
    """

    ERROR = None
    WARNING = None
    NAME = None

    def __init__(self):
        if not isinstance(getattr(self, "ERROR", None), str):
            raise ValueError(f"ERROR class-attribute of {self.__class__!r} not set or invalid.")
        if not isinstance(getattr(self, "NAME", None), str):
            raise ValueError(f"NAME class-attribute of {self.__class__!r} not set or invalid.")
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
        with suppress(Exception):
            cleaned_value = self.to_python(value)

        return errors, warnings, cleaned_value

    @staticmethod
    def _normalize_check_result(check_result, default):
        if check_result is None:
            raise ValueError("None is not an allowed value.")

        if check_result is False:
            return ()

        if check_result is True and default:
            check_result = (default,)

        if isinstance(check_result, str):
            check_result = (check_result,)

        if type(check_result) not in (list, tuple):
            raise ValueError("Error lists must be of type list or tuple.")

        for s in check_result:
            if not isinstance(s, str):
                raise ValueError("At least one non-string error was returned.")

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
        return f"<Field {self.name}>"


class NetworkField(Field):
    ERROR = "Not a valid IP network"
    ERROR_LOOPBACK = "Loopback network not allowed"
    ERROR_PRIVATE = "Private network not allowed"
    ERROR_RESERVED = "Reserved network not allowed"
    ERROR_MULTICAST = "Multicast network not allowed"
    NAME = "network"

    def _check_errors(self, value):
        try:
            net = self.to_python(value)
        except Exception:
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
    ERROR = "Not a valid ISO3166-1 country code"
    NAME = "country"

    def _check_errors(self, value):
        return bool(value and not self.to_python(value))

    def to_python(self, value):
        if value:
            return pycountry.countries.get(alpha_2=value)
        return None

    def to_string(self, value):
        if value:
            try:
                country = self.to_python(value)
                return country.alpha_2
            except Exception:
                pass
        return ""


class SubdivisionField(Field):
    ERROR = "Not a valid ISO3166-2 subdivision code"
    NAME = "subdivision"

    def _check_errors(self, value):
        return bool(value and not self.to_python(value))

    def to_python(self, value):
        if value:
            return pycountry.subdivisions.get(code=value)
        return None

    def to_string(self, value):
        if value:
            try:
                subdivision = self.to_python(value)
                return subdivision.code
            except Exception:
                pass
        return ""


class CityField(Field):
    ERROR = "unvalidated"
    NAME = "city"

    def _check_errors(self, value):
        # TODO: city is not validated right now
        return False

    def to_python(self, value):
        return value


class ZipCodeField(Field):
    ERROR = "unvalidated"
    NAME = "zipcode"

    def _check_errors(self, value):
        # TODO: zip code is not validated right now
        return False

    def to_python(self, value):
        return value
