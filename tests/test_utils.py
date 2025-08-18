# test/test_utils.py
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

import io
import unittest

from geofeed_validator import is_file_like_object

__all__ = ["IsFileLikeObjectTestCase"]


class IsFileLikeObjectTestCase(unittest.TestCase):
    def test_0000_not_file_like(self):
        self.assertEqual(False, is_file_like_object("test"))

    def test_0001_is_file_like(self):
        self.assertEqual(True, is_file_like_object(io.StringIO()))
