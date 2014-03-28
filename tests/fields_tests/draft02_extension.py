# test/fields_test/draft02_extension.py
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
from .base import FieldTestCaseMixin
from geofeed_validator.fields.draft02_extension import AllocationSizeField

__all__ = ['AllocationSizeFieldTestCase']

class AllocationSizeFieldTestCase(FieldTestCaseMixin, unittest.TestCase):
    FIELD_CLASS = AllocationSizeField

    def test_0000_invalid_cidr_notation(self):
        self.assertEqual(((AllocationSizeField.ERROR,), tuple(), None), self.field.validate('32'))

    def test_0001_valid_cidr_notation(self):
        self.assertEqual((tuple(), tuple(), 32), self.field.validate('/32'))

    def test_0002_empty_string(self):
        self.assertEqual((tuple(), tuple(), ''), self.field.validate(''))
