# Copyright (C) 2014 ANEXIA Internetdienstleistungs GmbH
# SPDX-FileCopyrightText: 2022 2014 ANEXIA Internetdienstleistungs GmbH Authors: Stephan Peijnik <speijnik@anexia-it.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from geofeed_validator.fields.draft02_extension import AllocationSizeField

from .test_base import FieldTestCaseMixin

__all__ = ["AllocationSizeFieldTestCase"]


class AllocationSizeFieldTestCase(FieldTestCaseMixin, unittest.TestCase):
    FIELD_CLASS = AllocationSizeField

    def test_0000_invalid_cidr_notation(self):
        self.assertEqual(
            ((AllocationSizeField.ERROR,), tuple(), None), self.field.validate("32")
        )

    def test_0001_valid_cidr_notation(self):
        self.assertEqual((tuple(), tuple(), 32), self.field.validate("/32"))

    def test_0002_empty_string(self):
        self.assertEqual((tuple(), tuple(), ""), self.field.validate(""))
