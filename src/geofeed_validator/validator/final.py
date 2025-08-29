# geofeed_validator/validator/final.py
#
# ANEXIA GeoFeed Validator
#
# Copyright (C) 2025 ANEXIA Internetdienstleistungs GmbH
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

from geofeed_validator.fields import Alpha2CodeField, CityFieldFinal, IPPrefixField, PostalCodeField, RegionField
from geofeed_validator.validator.base import BaseCSVValidator, Registry


class CSVValidatorFinal(BaseCSVValidator):
    NAME = "final"
    FIELDS = [IPPrefixField, Alpha2CodeField, RegionField, CityFieldFinal, PostalCodeField]

    # TODO: line breaks must be CRLF (RFC4180)


Registry.register(CSVValidatorFinal)
