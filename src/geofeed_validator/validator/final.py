# geofeed_validator/validator/final.py
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

from geofeed_validator.fields import Alpha2CodeField, CityField, IPPrefixField, PostalCodeField, RegionField
from geofeed_validator.validator.base import BaseCSVValidator, Registry


@Registry.register
class CSVValidatorFinal(BaseCSVValidator):
    NAME = "final"
    FIELDS = [IPPrefixField, Alpha2CodeField, RegionField, CityField, PostalCodeField]

    # line breaks must be CRLF (RFC4180)

    # mentions of planned extensions removed:
    # - no more delegation size
    # - no alternative formats
    # mentions of finding geolocation fields removed:
    # - no public authority
    # - no rdns records
    # -> well known uris still present
    #   - validated via bgp
    #
    # notes:
    # - demo validator in rfc
    # - list of test lines in rfc
    #   -> ensure they are included in the tests
    #
    # for ogf:
    # -> no ttl in format, but can be communicated via http standard headers
    # -> privacy and security:
    #   - precise zip code (to building) must only be published with permission of the party being located
    #   - should inform parties of privacy tradeoffs
    #   - may allow differentiation between used/unused prefixes
    #   - must validate source is allowed to publish prefix geofeed
    #     - depends on how feed was discovered
