# geofeed_validator/validator/draft02.py
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

from geofeed_validator.fields import NetworkField, CountryField, SubdivisionField, CityField, ZipCodeField
from geofeed_validator.fields.draft02_extension import AllocationSizeField
from geofeed_validator.validator.base import BaseCSVValidator, Registry


class CSVValidatorDraft02(BaseCSVValidator):
    NAME = 'draft02'
    FIELDS = [NetworkField, CountryField, SubdivisionField, CityField, ZipCodeField]

Registry.register(CSVValidatorDraft02)


class CSVValidatorDraft02WithAllocationSize(CSVValidatorDraft02):
    NAME = 'draft02-allocationsize'
    FIELDS = CSVValidatorDraft02.FIELDS + [AllocationSizeField]

    def _validate_common_extra(self, record):
        network = record.get_field_value(NetworkField)
        allocation_size = record.get_field_value(AllocationSizeField)
        if network and allocation_size:
            if allocation_size < 0:
                record.add_field_errors(AllocationSizeField, 'Allocation size must not be negative.')

            if network.version == 4 and allocation_size > 32:
                record.add_field_errors(AllocationSizeField, 'IPv4 prefix length is 32 bits at maximum.')
            elif network.version == 6 and allocation_size > 128:
                record.add_field_errors(AllocationSizeField, 'IPv6 prefix length is 128 bits at maximum.')

            if 0 <= allocation_size < network.prefixlen:
                record.add_field_errors(AllocationSizeField,
                                        'Default allocation size larger than network prefix length.')
            elif network.prefixlen == allocation_size:
                record.add_field_warnings(AllocationSizeField,
                                          'Network prefix length is equal to default allocation size.')

Registry.register(CSVValidatorDraft02WithAllocationSize)