# test/fields_test/base.py
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
import netaddr
import pycountry

from geofeed_validator.fields.base import Field, NetworkField, CountryField, SubdivisionField, CityField, ZipCodeField

__all__ = ['FieldTestCase', 'NetworkFieldTestCase', 'CountryFieldTestCase', 'SubdivisionFieldTestCase',
           'ZipCodeFieldTestCase']

class FieldTestCase(unittest.TestCase):
    def test_0000_init_no_error(self):
        class TestField(Field):
            pass

        self.assertRaises(ValueError, TestField)

    def test_0001_init_no_name(self):
        class TestField(Field):
            ERROR = 'test_error'

        self.assertRaises(ValueError, TestField)

    def test_0002_name_property(self):
        class TestField(Field):
            ERROR = 'test_error'
            NAME = 'test_field'

        test_field = TestField()
        self.assertEqual('test_field', test_field.name)

    def test_0003_check_errors_not_implemented(self):
        class TestField(Field):
            ERROR = 'test_error'
            NAME = 'test_field_no_check_errors'

        test_field = TestField()
        self.assertRaises(NotImplementedError, test_field._check_errors, None)

    def test_0004_check_warnings_default_false(self):
        class TestField(Field):
            ERROR = 'test_error'
            NAME = 'test_field_no_check_warnings'


        test_field = TestField()
        self.assertEqual(False, test_field._check_warnings(None))

    def test_0005_to_python_not_implemented(self):
        class TestField(Field):
            ERROR = 'test_error'
            NAME = 'test_field_no_to_python'

        test_field = TestField()
        self.assertRaises(NotImplementedError, test_field.to_python, None)

    def test_0006_check_errors_default_error(self):
        class TestField(Field):
            ERROR = 'test_error'
            NAME = 'test_field'

            def _check_errors(self, value):
                return True

            def to_python(self, value):
                raise ValueError('test')

        test_field = TestField()
        self.assertEqual(((TestField.ERROR,), tuple(), None), test_field.validate(None))

    def test_0007_repr(self):
        class TestField(Field):
            ERROR = 'test_error'
            NAME = 'test_field'

        test_field = TestField()
        self.assertEqual(repr(test_field), '<Field test_field>')

    def test_0008_check_errors_not_list_tuple(self):
        class TestField(Field):
            ERROR = 'test_error'
            NAME = 'test_field'

            def _check_errors(self, value):
                return dict()

        test_field = TestField()
        self.assertRaises(ValueError, test_field.validate, None)

    def test_0009_check_errors_not_none(self):
        class TestField(Field):
            ERROR = 'test_error'
            NAME = 'test_field'

            def _check_errors(self, value):
                return None

        test_field = TestField()
        self.assertRaises(ValueError, test_field.validate, None)

    def test_0010_check_errors_non_string(self):
        class TestField(Field):
            ERROR = 'test_error'
            NAME = 'test_field'

            def _check_errors(self, value):
                return ('a', False)

        test_field = TestField()
        self.assertRaises(ValueError, test_field.validate, None)

    def test_0011_check_errors_string(self):
        class TestField(Field):
            ERROR = 'test_error'
            NAME = 'test_field'

            def to_python(self, value):
                return value

            def _check_errors(self, value):
                return 'error_string'

        test_field = TestField()
        self.assertEqual((('error_string',), tuple(), None), test_field.validate(None))

    def test_0012_to_string_exception(self):
        class TestField(Field):
            ERROR = 'test_error'
            NAME = 'test_field'

        test_field = TestField()
        self.assertEqual(None, test_field.to_string('test_string'))

    def test_0012_to_string_valid(self):
        class TestField(Field):
            ERROR = 'test_error'
            NAME = 'test_field'

            def to_python(self, value):
                return value

        test_field = TestField()
        self.assertEqual('test_string', test_field.to_string('test_string'))


class FieldTestCaseMixin(object):
    FIELD_CLASS = None
    field = None

    def setUp(self):
        self.field = self.FIELD_CLASS()

    def tearDown(self):
        if self.field:
            self.field = None


class NetworkFieldTestCase(FieldTestCaseMixin, unittest.TestCase):
    FIELD_CLASS = NetworkField

    def test_0001_invalid_value(self):
        self.assertEqual(((NetworkField.ERROR,), tuple(), None), self.field.validate(1))

    def test_0002_loopback(self):
        self.assertEqual(((NetworkField.ERROR_LOOPBACK, ), tuple(), netaddr.IPNetwork('127.0.0.1/32')),
                         self.field.validate('127.0.0.1'))

    def test_0003_multicast(self):
        self.assertEqual(((NetworkField.ERROR_MULTICAST, ), tuple(), netaddr.IPNetwork('224.0.0.1/32')),
                         self.field.validate('224.0.0.1/32'))

    def test_0004_private(self):
        self.assertEqual(((NetworkField.ERROR_PRIVATE, ), tuple(), netaddr.IPNetwork('192.168.0.0/24')),
                         self.field.validate('192.168.0.0/24'))

    def test_0005_reserved(self):
        self.assertEqual(((NetworkField.ERROR_RESERVED, ), tuple(), netaddr.IPNetwork('192.0.0.0/24')),
                         self.field.validate('192.0.0.0/24'))

    def test_0006_valid(self):
        self.assertEqual((tuple(), tuple(), netaddr.IPNetwork('8.8.8.8')),
                         self.field.validate('8.8.8.8'))


class CountryFieldTestCase(FieldTestCaseMixin, unittest.TestCase):
    FIELD_CLASS = CountryField

    def test_0001_invalid_alpha2(self):
        self.assertEqual(((CountryField.ERROR, ), tuple(), None), self.field.validate('INVALID'))

    def test_0002_valid_alpha2(self):
        self.assertEqual((tuple(), tuple(), pycountry.countries.get(alpha2='AT')), self.field.validate('AT'))

    def test_0004_to_string_valid(self):
        self.assertEqual('AT', self.field.to_string('AT'))

    def test_0005_to_string_invalid(self):
        self.assertEqual('', self.field.to_string('INVALID'))

    def test_0006_to_string_empty(self):
        self.assertEqual('', self.field.to_string(None))

    def test_0007_to_python_empty(self):
        self.assertEqual(None, self.field.to_python(None))


class SubdivisionFieldTestCase(FieldTestCaseMixin, unittest.TestCase):
    FIELD_CLASS = SubdivisionField

    def test_0001_invalid_alpha2(self):
        self.assertEqual(((SubdivisionField.ERROR, ), tuple(), None), self.field.validate('INVALID'))

    def test_0002_valid_alpha2(self):
        self.assertEqual((tuple(), tuple(), pycountry.subdivisions.get(code='AT-1')), self.field.validate('AT-1'))

    def test_0004_to_string_valid(self):
        self.assertEqual('AT-1', self.field.to_string('AT-1'))

    def test_0005_to_string_invalid(self):
        self.assertEqual('', self.field.to_string('INVALID'))

    def test_0006_to_string_empty(self):
        self.assertEqual('', self.field.to_string(None))

    def test_0007_to_python_empty(self):
        self.assertEqual(None, self.field.to_python(None))


class UnimplementedFieldTestCaseMixin(FieldTestCaseMixin):
    def test_0001_to_python_verbatim(self):
        self.assertEqual('test', self.field.to_python('test'))

    def test_0002_check_errors_false(self):
        self.assertEqual(False, self.field._check_errors(None))
        self.assertEqual(False, self.field._check_errors(True))
        self.assertEqual(False, self.field._check_errors(False))
        self.assertEqual(False, self.field._check_errors('test'))


class CityFieldTestCase(UnimplementedFieldTestCaseMixin, unittest.TestCase):
    FIELD_CLASS = CityField


class ZipCodeFieldTestCase(UnimplementedFieldTestCaseMixin, unittest.TestCase):
    FIELD_CLASS = ZipCodeField