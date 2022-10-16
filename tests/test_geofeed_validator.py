# Copyright (C) 2014 ANEXIA Internetdienstleistungs GmbH
# SPDX-FileCopyrightText: 2022 2014 ANEXIA Internetdienstleistungs GmbH Authors: Stephan Peijnik <speijnik@anexia-it.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import io
import unittest

from geofeed_validator import GeoFeedValidator
from geofeed_validator.result import ValidationResult
from geofeed_validator.validator import BaseValidator, Registry

__all__ = ["GeoFeedValidatorTestCase"]


class GeoFeedValidatorTestCase(unittest.TestCase):
    def test_0000_init_invalid_validator(self):
        class TestClass(object):
            pass

        self.assertRaises(ValueError, GeoFeedValidator, "", validator=1)
        self.assertRaises(KeyError, GeoFeedValidator, "", validator="INVALID")
        self.assertRaises(ValueError, GeoFeedValidator, "", validator=TestClass)

    def test_0001_init_default_validator(self):
        validator = GeoFeedValidator("", validator=None)
        self.assertEqual(GeoFeedValidator.DEFAULT_VALIDATOR, validator._validator_name)
        self.assertEqual(
            Registry.find(GeoFeedValidator.DEFAULT_VALIDATOR), validator._validator
        )

    def test_0002_init_by_name(self):
        for name in Registry.names():
            validator = GeoFeedValidator("", validator=name)
            self.assertEqual(name, validator._validator_name)
            self.assertEqual(Registry.find(name), validator._validator)

    def test_0003_init_by_class(self):
        class Validator(BaseValidator):
            NAME = "TestValidator"
            FIELDS = ()

        validator = GeoFeedValidator("", validator=Validator)
        self.assertEqual(Validator.NAME, validator._validator_name)
        self.assertEqual(Validator, validator._validator)

    def test_0004_init_filelike(self):
        tv = GeoFeedValidator(io.StringIO())

    def test_0005_init_string(self):
        tv = GeoFeedValidator("")

    def test_0006_init_invalid(self):
        class TestClass(object):
            pass

        self.assertRaises(ValueError, GeoFeedValidator, TestClass())
        self.assertRaises(ValueError, GeoFeedValidator, TestClass)

    def test_0007_validate(self):
        validator = GeoFeedValidator("")
        res = validator.validate()
        self.assertIsInstance(res, ValidationResult)
        self.assertTrue(res.is_valid(allow_warnings=False))

    def test_0008_validate_by_is_valid(self):
        validator = GeoFeedValidator("")
        self.assertTrue(validator.is_valid(allow_warnings=False))
        self.assertIsInstance(validator.validate(), ValidationResult)

    def test_0009_record_name(self):
        validator = GeoFeedValidator("")
        self.assertEqual("???", validator.record_name)
        validator.validate()
        self.assertEqual(validator._validator.RECORD_NAME, validator.record_name)

    def test_0010_fields(self):
        validator = GeoFeedValidator("")
        self.assertEqual(list(), validator.fields)
        validator.validate()
        self.assertEqual(validator._validator.FIELDS, validator.fields)
