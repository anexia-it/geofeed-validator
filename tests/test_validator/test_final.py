# test/test_validator/test_draft02.py
#
# ANEXIA GeoFeed Validator
#
# Copyright (C) 2025 ANEXIA Internetdienstleistungs GmbH
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
# Gerhard Bogner <gbogner@anexia-it.com>
#
from ipaddress import ip_network

from pytest import mark

from geofeed_validator.fields.final import Alpha2CodeField
from geofeed_validator.validator import CSVValidatorFinal


@mark.parametrize(
    ("line", "error_count", "warning_count"),
    (
        ("# asdf", 0, 0),
        ("   ", 0, 0),
        ("", 0, 0),
        ("asdf", 1, 1),
        ("asdf,US,,,", 1, 0),
        ("aaaa::,US,,,", 0, 0),
        ("zzzz::,US", 1, 1),
        (",US,,,", 1, 0),
        ("55.66.77", 1, 1),
        ("55.66.77.888", 1, 1),
        ("55.66.77.asdf", 1, 1),
        ("2001:db8:cafe::/48,PL,PL-14,,02-784", 0, 0),  # PL-MZ changed to PL-14 on 2018-11-26
        ("2001:db8:cafe::/48", 0, 1),
        ("55.66.77.88,PL", 0, 1),
        ("55.66.77.88,PL,,,", 0, 0),
        ("55.66.77.88,,,,", 0, 0),
        ("55.66.77.88,ZZ,,,", 0, 0),
        ("55.66.77.88,US,,,", 0, 0),
        ("55.66.77.88,USA,,,", 1, 0),
        ("55.66.77.88,99,,,", 1, 0),
        ("55.66.77.88,US,US-CA,,", 0, 0),
        ("55.66.77.88,US,USA-CA,,", 1, 0),
        ("55.66.77.88,USA,USA-CA,,", 2, 0),
        ("55.66.77.88,US,US-CA,Mountain View,", 0, 0),
        ("55.66.77.88,US,US-CA,Mountain View,94043", 0, 0),
        ("55.66.77.88,US,US-CA,Mountain View,94043,1600 Ampthitheatre Parkway", 0, 1),
        ("55.66.77.0/24,US,,,", 0, 0),
        ("55.66.77.88/24,US,,,", 1, 0),
        ("55.66.77.88/32,US,,,", 0, 0),
        ("55.66.77/24,US,,,", 1, 0),
        ("55.66.77.0/35,US,,,", 1, 0),
        ("172.15.30.1,US,,,", 0, 0),
        ("172.28.30.1,US,,,", 1, 0),
        ("192.167.100.1,US,,,", 0, 0),
        ("192.168.100.1,US,,,", 1, 0),
        ("10.0.5.9,US,,,", 1, 0),
        ("10.0.5.0/24,US,,,", 1, 0),
        ("fc00::/48,PL,,,", 1, 0),
        ("fe00::/48,PL,,,", 0, 0),
    ),
)
@staticmethod
def test_rfc_lines(error_count: int, line: str, warning_count: int) -> None:
    validator = CSVValidatorFinal(line)
    result = validator.validate()

    fields = line.split(",")
    if not fields[0].strip().startswith("#") and line.strip():
        try:
            ip_prefix = ip_network(fields[0])
        except ValueError:
            pass
        else:
            if (
                # goefeed_validator checks for reserved in addition to private prefixes
                not ip_prefix.is_private
                and ip_prefix.is_reserved
                # geofeed_validator checks for prefixes reserved for documentation
                or ip_prefix.is_private
                and ip_prefix.version == 6
                and ip_network("2001:db8::/32").supernet_of(ip_prefix)
            ):
                error_count += 1

        if len(fields) >= 5 and fields[4]:
            # geofeed_validator warns about using the deprecated postal_code field
            warning_count += 1
        if len(fields) < 5:
            # rfc test lines count missing as a single warning
            warning_count += 4 - len(fields)
        elif len(fields) > 5:
            # rfc test lines count extra fields as a single warning
            warning_count -= 1
        if len(fields) >= 2 and Alpha2CodeField()._check_warnings(fields[1]):
            # rfc test lines do not count non-ISO3316-1 alpha-2 values as warnings
            warning_count += 1

    assert result.error_count == error_count, "error count differs"
    assert result.warning_count == warning_count, "warning count differs"
