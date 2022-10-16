# Copyright (C) 2014 ANEXIA Internetdienstleistungs GmbH
# SPDX-FileCopyrightText: 2022 2014 ANEXIA Internetdienstleistungs GmbH Authors: Stephan Peijnik <speijnik@anexia-it.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from geofeed_validator.fields import (
    CityField,
    CountryField,
    NetworkField,
    SubdivisionField,
    ZipCodeField,
)
from geofeed_validator.fields.draft02_extension import AllocationSizeField
from geofeed_validator.validator.base import BaseCSVValidator, Registry


class CSVValidatorDraft02(BaseCSVValidator):
    NAME = "draft02"
    FIELDS = [NetworkField, CountryField, SubdivisionField, CityField, ZipCodeField]


Registry.register(CSVValidatorDraft02)


class CSVValidatorDraft02WithAllocationSize(CSVValidatorDraft02):
    NAME = "draft02-allocationsize"
    FIELDS = CSVValidatorDraft02.FIELDS + [AllocationSizeField]

    def _validate_common_extra(self, record):
        network = record.get_field_value(NetworkField)
        allocation_size = record.get_field_value(AllocationSizeField)
        if network and allocation_size:
            if allocation_size < 0:
                record.add_field_errors(
                    AllocationSizeField, "Allocation size must not be negative."
                )

            if network.version == 4 and allocation_size > 32:
                record.add_field_errors(
                    AllocationSizeField, "IPv4 prefix length is 32 bits at maximum."
                )
            elif network.version == 6 and allocation_size > 128:
                record.add_field_errors(
                    AllocationSizeField, "IPv6 prefix length is 128 bits at maximum."
                )

            if 0 <= allocation_size < network.prefixlen:
                record.add_field_errors(
                    AllocationSizeField,
                    "Default allocation size larger than network prefix length.",
                )
            elif network.prefixlen == allocation_size:
                record.add_field_warnings(
                    AllocationSizeField,
                    "Network prefix length is equal to default allocation size.",
                )


Registry.register(CSVValidatorDraft02WithAllocationSize)
