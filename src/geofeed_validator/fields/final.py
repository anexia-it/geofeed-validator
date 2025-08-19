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
# Gerhard Bogner <gbogner@anexia-it.com>
#

from pycountry import countries

from geofeed_validator.fields import CountryField, NetworkField, SubdivisionField, ZipCodeField


class Alpha2CodeField(CountryField):
    ERROR = "Not a valid ISO3166-1 alpha-2 code"
    NAME = "alpha2code"
    WARNING = "Not an assigned ISO3316-1 alpha-2 code"

    def _check_errors(self, value: str) -> bool:
        return not (len(value) == 2 and value.isalpha() and value.isascii())

    def _check_warnings(self, value: str) -> bool:
        return bool(value and not self.to_python(value))

    def to_python(self, value):
        return countries.get(alpha_2=value.upper()) if value else None


class IPPrefixField(NetworkField):
    ERROR = NetworkField.ERROR.replace("network", "prefix")
    ERROR_LOOPBACK = NetworkField.ERROR_LOOPBACK.replace("network", "IP prefix")
    ERROR_PRIVATE = NetworkField.ERROR_PRIVATE.replace("network", "IP prefix")
    ERROR_RESERVED = NetworkField.ERROR_RESERVED.replace("network", "IP prefix")
    ERROR_MULTICAST = NetworkField.ERROR_MULTICAST.replace("network", "IP prefix")
    NAME = "ip_prefix"


class PostalCodeField(ZipCodeField):
    NAME = "postal_code"
    WARNING = "This field is deprecated and should no longer be used"

    def _check_errors(self, value):
        return False

    def _check_warnings(self, value):
        return bool(value.strip())


class RegionField(SubdivisionField):
    NAME = "region"
