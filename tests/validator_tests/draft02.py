# test/validator_tests/base.py
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
import unittest
from geofeed_validator.validator import CSVValidatorDraft02WithAllocationSize

__all__ = ['CSVValidatorDraft02WithAllocationSizeTestCase']

class CSVValidatorDraft02WithAllocationSizeTestCase(unittest.TestCase):
    def test_0000_allocation_size_extension(self):
        validator = CSVValidatorDraft02WithAllocationSize('''8.8.8.0/29,,,,,/-1
        8.8.9.0/29,,,,,/33
        2001::/64,,,,,/129
        8.8.10.0/29,,,,,/24
        8.8.11.0/29,,,,,/29''', store_raw_records=True)

        res = validator.validate()

        self.assertFalse(res.is_valid(allow_warnings=True))
        self.assertEqual(4, res.error_count)
        self.assertEqual(1, res.warning_count)
        r0, r1, r2, r3, r4 = res.records

        r0_as_field = r0.get_field_result('allocation_size')
        r1_as_field = r1.get_field_result('allocation_size')
        r2_as_field = r2.get_field_result('allocation_size')
        r3_as_field = r3.get_field_result('allocation_size')
        r4_as_field = r4.get_field_result('allocation_size')

        self.assertEqual(1, len(r0_as_field.errors))
        self.assertEqual(1, len(r1_as_field.errors))
        self.assertEqual(1, len(r2_as_field.errors))
        self.assertEqual(1, len(r3_as_field.errors))
        self.assertEqual(0, len(r4_as_field.errors))

        self.assertEqual(['Allocation size must not be negative.'], r0_as_field.errors)
        self.assertEqual(['IPv4 prefix length is 32 bits at maximum.'], r1_as_field.errors)
        self.assertEqual(['IPv6 prefix length is 128 bits at maximum.'], r2_as_field.errors)
        self.assertEqual(['Default allocation size larger than network prefix length.'], r3_as_field.errors)

        self.assertEqual(0, len(r0_as_field.warnings))
        self.assertEqual(0, len(r1_as_field.warnings))
        self.assertEqual(0, len(r2_as_field.warnings))
        self.assertEqual(0, len(r3_as_field.warnings))
        self.assertEqual(1, len(r4_as_field.warnings))

        self.assertEqual(['Network prefix length is equal to default allocation size.'], r4_as_field.warnings)
