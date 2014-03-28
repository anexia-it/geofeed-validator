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
import cStringIO
from geofeed_validator import BaseValidator, Registry
from geofeed_validator.fields import NetworkField, ZipCodeField, CityField, SubdivisionField, CountryField
from geofeed_validator.validator import BaseCSVValidator

__all__ = ['BaseCSVValidatorTestCase', 'BaseValidatorTestCase', 'RegistryTestCase']


class BaseValidatorTestCase(unittest.TestCase):
    def test_0000_init(self):
        class TestValidator(BaseValidator):
            pass

        self.assertRaises(ValueError, TestValidator, '')

        class TestValidator2(BaseValidator):
            NAME = 'test'

        self.assertRaises(ValueError, TestValidator2, '')

        class TestValidator3(BaseValidator):
            NAME = 'test'
            FIELDS = (1,)

        self.assertRaises(ValueError, TestValidator3, '')

        class TestValidator4(BaseValidator):
            NAME = 'test'
            FIELDS = (NetworkField,)

        tv = TestValidator4('')
        tv = TestValidator4(cStringIO.StringIO(''))
        self.assertRaises(ValueError, TestValidator4, None)

    def test_0001_get_records_unimplemented(self):

        class TestValidator(BaseValidator):
            NAME = 'test'
            FIELDS = (NetworkField,)

        tv = TestValidator('')
        self.assertRaises(NotImplementedError, tv.get_records)

    def test_0002_empty_feed_validation(self):
        class TestValidator(BaseValidator):
            NAME = 'test'
            FIELDS = (NetworkField,)

            def get_records(self):
                return [({},''),]

        tv = TestValidator('')
        res = tv.validate()
        self.assertTrue(res.is_valid(allow_warnings=False))

    def test_0003_duplicate_network(self):
        nw_field = NetworkField()

        class TestValidator(BaseValidator):
            NAME = 'test'
            FIELDS = (nw_field,)

            def get_records(self):
                return [
                    (
                        {nw_field: '8.8.8.0/24'}, '8.8.8.0/24'
                    ),
                    (
                        {nw_field: '8.8.8.0/24'}, '8.8.8.0/24'
                    )
                ]

        tv = TestValidator('')
        res = tv.validate()
        self.assertFalse(res.is_valid(allow_warnings=True))
        records = res.records
        self.assertEqual(2, len(records))
        self.assertEqual(2, res.error_count)
        self.assertEqual(0, res.warning_count)
        first_record = records[0]
        second_record = records[1]
        self.assertEqual(1, first_record.error_count)
        self.assertEqual(1, second_record.error_count)
        self.assertEqual(['Duplicate of record #1'], first_record.get_field_result(nw_field).errors)
        self.assertEqual(['Duplicate of record #0'], second_record.get_field_result(nw_field).errors)

    def test_0004_missing_geo_info(self):
        fields = (CountryField(), SubdivisionField(), CityField(), ZipCodeField())
        c_field, sd_field, city_field, zc_field = fields

        class TestValidator(BaseValidator):
            NAME = 'test'
            FIELDS = fields

            def get_records(self):
                return [
                    (
                        # First case: subdivision w/out country
                        {c_field: '', sd_field: 'AT-1', city_field: '', zc_field: ''},
                        ',AT-1,,'
                    ),
                    (
                        # Second case: city w/out country
                        {c_field: '', sd_field: '', city_field: 'Test', zc_field: ''},
                        ',,Test,'
                    ),
                    (
                        # Third case: zipcode w/out country
                        {c_field: '', sd_field: '', city_field: '', zc_field: 'Test'},
                        ',,,Test'
                    ),
                    (
                        # Fourth case: country/subdivision mismatch
                        {c_field: 'DE', sd_field: 'AT-1', city_field: '', zc_field: ''},
                        'DE,AT-1,,'
                    )
                ]

        tv = TestValidator('')
        res = tv.validate()
        self.assertFalse(res.is_valid(allow_warnings=True))
        case1_record, case2_record, case3_record, case4_record = res.records
        self.assertEqual(4, res.error_count)
        self.assertEqual(0, res.warning_count)
        for r in res.records:
            self.assertEqual(1, r.error_count)
            self.assertEqual(0, r.warning_count)

        self.assertEqual(['Subdivision specified, but country missing/invalid.'],
                         case1_record.get_field_result(SubdivisionField).errors)
        self.assertEqual(['City specified, but country missing/invalid.'],
                         case2_record.get_field_result(CityField).errors)
        self.assertEqual(['Zipcode specified, but country missing/invalid.'],
                         case3_record.get_field_result(ZipCodeField).errors)
        self.assertEqual(['Subdivision not a subdivison of given country.'],
                         case4_record.get_field_result(SubdivisionField).errors)


class RegistryTestCase(unittest.TestCase):
    def test_0000_register_invalid_class(self):
        class Test(object):
            pass

        self.assertRaises(ValueError, Registry.register, Test)

    def test_0001_register_no_name(self):
        class Test(BaseValidator):
            pass

        self.assertRaises(ValueError, Registry.register, Test)

    def test_0002_register_valid(self):
        class Test(BaseValidator):
            NAME = 'TEST'

        Registry.register(Test)
        self.assertIn('TEST', Registry.names())
        del Registry.VALIDATORS['TEST']

    def test_0003_find_unknown(self):
        self.assertRaises(KeyError, Registry.find, 'TEST')

    def test_0004_find_known(self):
        class Test(BaseValidator):
            NAME = 'TEST'

        Registry.register(Test)
        self.assertIn('TEST', Registry.names())
        self.assertEqual(Test, Registry.find('TEST'))
        del Registry.VALIDATORS['TEST']


class BaseCSVValidatorTestCase(unittest.TestCase):
    def test_000_valid_csv(self):
        fields = (NetworkField(), CountryField(), SubdivisionField())
        nw_field, c_field, sd_field = fields

        class TestValidator(BaseCSVValidator):
            NAME = 'TEST'
            FIELDS = fields

        tv = TestValidator('# test comment\n1,2,3\n4,5,6,7')
        (cmt_fields, cmt_raw), (first_fields, first_raw), (second_fields, second_raw) = [r for r in tv.get_records()]
        self.assertEqual({}, cmt_fields)
        self.assertEqual('# test comment', cmt_raw)
        self.assertEqual('1,2,3', first_raw)
        self.assertEqual('4,5,6,7', second_raw)
        self.assertEqual({nw_field: '1', c_field: '2', sd_field: '3'}, first_fields)
        self.assertEqual({nw_field: '4', c_field: '5', sd_field: '6', '__extra__': ['7']}, second_fields)