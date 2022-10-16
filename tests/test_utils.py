# Copyright (C) 2014 ANEXIA Internetdienstleistungs GmbH
# SPDX-FileCopyrightText: 2022 2014 ANEXIA Internetdienstleistungs GmbH Authors: Stephan Peijnik <speijnik@anexia-it.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import io
import unittest

from geofeed_validator import is_file_like_object

__all__ = ["IsFileLikeObjectTestCase"]


class IsFileLikeObjectTestCase(unittest.TestCase):
    def test_0000_not_file_like(self):
        self.assertEqual(False, is_file_like_object("test"))

    def test_0001_is_file_like(self):
        self.assertEqual(True, is_file_like_object(io.StringIO()))
