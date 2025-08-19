# test/test_result.py
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

import unittest

import netaddr

from geofeed_validator.fields import (
    CityField,
    NetworkField,
    SubdivisionField,
    ZipCodeField,
)
from geofeed_validator.result import (
    FieldResult,
    RecordValidationResult,
    ValidationResult,
)

__all__ = [
    "FieldResultTestCase",
    "RecordValidationResultTestCase",
    "ValidationResultTestCase",
]


class FieldResultTestCase(unittest.TestCase):
    def test_0000_params_verbatim(self):
        # In this test it is safe to use integers, we just want to make sure that all
        # attributes are initialized in order.
        res = FieldResult(1, 2, 3, 4, 5, 6)
        self.assertEqual(res.field, 1)
        self.assertEqual(res.value, 2)
        self.assertEqual(res.errors, 3)
        self.assertEqual(res.warnings, 4)
        self.assertEqual(res.raw, 5)
        self.assertEqual(res.value_string, 6)

    def test_0001_getstate_setstate(self):
        res = FieldResult(
            NetworkField(),
            netaddr.IPNetwork("127.0.0.0/8"),
            (),
            (),
            "",
            "127.0.0.0/8",
        )

        state = res.__getstate__()
        self.assertNotIn("value", state)

        state["value_string"] = "192.168.0.0/24"
        res.__setstate__(state)
        self.assertEqual(netaddr.IPNetwork("192.168.0.0/24"), res.value)

        state["value_string"] = "INVALID"
        res.__setstate__(state)
        self.assertEqual(None, res.value)


class RecordValidationResultTestCase(unittest.TestCase):
    def test_0000_valid_record(self):
        nw_field = NetworkField()
        res = RecordValidationResult(
            123,
            (nw_field,),
            {nw_field: "8.8.8.0/24", "__extra__": ["test_extra"]},
            "8.8.8.0/24",
        )
        self.assertEqual(123, res.record_no)
        self.assertEqual(["test_extra"], res.extra)
        self.assertEqual(1, res.extra_offset)
        self.assertEqual("8.8.8.0/24", res.raw)

        res.validate()
        field_results = res.field_results
        self.assertEqual(1, len(field_results))
        self.assertEqual(False, res.was_ignored)
        self.assertEqual(0, res.warning_count)
        self.assertEqual(0, res.error_count)
        network_field_result = field_results[0]
        self.assertEqual(nw_field, network_field_result.field)
        self.assertEqual(netaddr.IPNetwork("8.8.8.0/24"), network_field_result.value)

    def test_0001_ignore_record(self):
        nw_field = NetworkField()
        res = RecordValidationResult(234, (nw_field,), {}, "")

        res.validate()
        self.assertEqual(True, res.was_ignored)
        self.assertEqual(0, res.error_count)
        self.assertEqual(0, res.warning_count)

    def test_0002_missing_field(self):
        nw_field = NetworkField()
        city_field = CityField()

        res = RecordValidationResult(456, (nw_field, city_field), {nw_field: "8.8.8.0/24"}, "8.8.8.0/24")

        res.validate()
        nw_field_result = res.get_field_result("network")
        city_field_result = res.get_field_result(city_field)

        self.assertEqual(0, len(nw_field_result.errors))

        self.assertEqual(netaddr.IPNetwork("8.8.8.0/24"), nw_field_result.value)
        self.assertEqual(netaddr.IPNetwork("8.8.8.0/24"), res.get_field_value("network"))
        self.assertEqual(netaddr.IPNetwork("8.8.8.0/24"), res.get_field_value(nw_field))

        self.assertEqual(1, len(city_field_result.errors))
        self.assertEqual(None, city_field_result.value)
        self.assertEqual(["Field is missing."], city_field_result.errors)
        self.assertEqual(None, res.get_field_value("city"))
        self.assertEqual(None, res.get_field_value(city_field))

        self.assertTrue(res.has_errors)
        self.assertFalse(res.has_warnings)
        self.assertEqual(1, res.error_count)
        self.assertEqual(0, res.warning_count)

    def test_0003_get_field_result_invalid(self):
        nw_field = NetworkField()
        city_field = CityField()

        res = RecordValidationResult(456, (nw_field, city_field), {nw_field: "8.8.8.0/24"}, "8.8.8.0/24")

        res.validate()
        self.assertEqual(None, res.get_field_result("subdivision"))
        self.assertEqual(None, res.get_field_value("subdivision"))


class ValidationResultTestCase(unittest.TestCase):
    def test_0000_no_store_records(self):
        nw_field = NetworkField()
        city_field = CityField()

        vr = ValidationResult((nw_field, city_field), store_raw_records=False)
        vr.add_record({nw_field: "8.8.8.0/24"}, "8.8.8.0/24")

        self.assertFalse(vr.is_valid())
        self.assertEqual(1, vr.error_count)
        self.assertEqual(0, vr.warning_count)
        self.assertEqual([], vr.records_raw)
        self.assertEqual(1, len(vr.records))
        self.assertEqual((nw_field, city_field), vr.fields)

    def test_0001_store_records(self):
        nw_field = NetworkField()
        city_field = CityField()

        vr = ValidationResult((nw_field, city_field), store_raw_records=True)
        vr.add_record({nw_field: "8.8.8.0/24"}, "8.8.8.0/24")
        vr.add_record({nw_field: "8.8.8.1/32"}, "8.8.8.1/32")

        self.assertFalse(vr.is_valid())
        self.assertEqual(2, vr.error_count)
        self.assertEqual(0, vr.warning_count)
        self.assertEqual(2, len(vr.records))
        self.assertEqual(["8.8.8.0/24", "8.8.8.1/32"], vr.records_raw)
        self.assertEqual((nw_field, city_field), vr.fields)

    def test_0002_is_valid_allow_warnings(self):
        nw_field = NetworkField()

        vr = ValidationResult((nw_field,), store_raw_records=True)
        vr.add_record({nw_field: "8.8.8.0/24"}, "8.8.8.0/24")
        vr.add_record({nw_field: "8.8.8.1/32"}, "8.8.8.1/32")
        for record in vr.records:
            record.add_field_warnings(nw_field, "test_warning")

        self.assertTrue(vr.is_valid(allow_warnings=True))
        self.assertFalse(vr.is_valid(allow_warnings=False))
        self.assertEqual(0, vr.error_count)
        self.assertEqual(2, vr.warning_count)
        self.assertEqual(2, len(vr.records))
        self.assertEqual(["8.8.8.0/24", "8.8.8.1/32"], vr.records_raw)
        self.assertEqual((nw_field,), vr.fields)

    def test_0003_add_field_warnings_add_field_errors(self):
        nw_field = NetworkField()
        city_field = CityField()
        zipcode_field = ZipCodeField()
        subdivision_field = SubdivisionField()

        vr = ValidationResult((nw_field, city_field), store_raw_records=True)
        vr.add_record({nw_field: "8.8.8.0/24"}, "8.8.8.0/24")
        vr.add_record({nw_field: "8.8.8.1/32"}, "8.8.8.1/32")

        self.assertFalse(vr.is_valid())
        self.assertEqual(2, vr.error_count)
        self.assertEqual(0, vr.warning_count)
        self.assertEqual(2, len(vr.records))
        self.assertEqual(["8.8.8.0/24", "8.8.8.1/32"], vr.records_raw)
        self.assertEqual((nw_field, city_field), vr.fields)

        records = vr.records
        # 2 errors: base
        # 0 warnings: base
        for record in records:
            record.add_field_errors(nw_field, "test_error")  # 2 more errors
            record.add_field_errors(city_field, ["test_error1", "test_error2"])  # 4 more errors
            record.add_field_warnings(nw_field, "test_warning")  # 2 more warnings
            record.add_field_warnings(city_field, ["test_warning1", "test_warning2"])  # 4 more warnings
            record.add_field_errors(zipcode_field, ("test_error3",))  # 2 more errors
            record.add_field_warnings(subdivision_field, ("test_warning3",))  # 2 more warnings

        self.assertFalse(vr.is_valid())
        self.assertEqual(10, vr.error_count)
        self.assertEqual(8, vr.warning_count)

        for record in records:
            self.assertTrue(record.has_errors)
            self.assertEqual(5, record.error_count)
            self.assertEqual(4, record.warning_count)
            self.assertFalse(record.was_ignored)

            nw_field_result = record.get_field_result("network")
            self.assertEqual(1, len(nw_field_result.errors))
            self.assertEqual(1, len(nw_field_result.warnings))
            self.assertEqual(["test_error"], nw_field_result.errors)
            self.assertEqual(["test_warning"], nw_field_result.warnings)

            city_field_result = record.get_field_result(city_field)
            self.assertEqual(3, len(city_field_result.errors))
            self.assertEqual(2, len(city_field_result.warnings))
            self.assertEqual(
                ["Field is missing.", "test_error1", "test_error2"],
                city_field_result.errors,
            )
            self.assertEqual(["test_warning1", "test_warning2"], city_field_result.warnings)

            zipcode_field_result = record.get_field_result(zipcode_field)
            self.assertEqual(1, len(zipcode_field_result.errors))
            self.assertEqual(0, len(zipcode_field_result.warnings))
            self.assertEqual(["test_error3"], zipcode_field_result.errors)

            subdivision_field_result = record.get_field_result(subdivision_field)
            self.assertEqual(0, len(subdivision_field_result.errors))
            self.assertEqual(1, len(subdivision_field_result.warnings))
            self.assertEqual(["test_warning3"], subdivision_field_result.warnings)
