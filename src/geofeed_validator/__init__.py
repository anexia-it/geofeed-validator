# geofeed_validator/__init__.py
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
# Stephan Peijnik <speijnik@anexia-it.com>
#


import inspect
import io

from geofeed_validator.utils import is_file_like_object
from geofeed_validator.validator.base import BaseValidator, Registry

__version__ = "0.6.1"


class GeoFeedValidator:
    """
    Validator class
    """

    DEFAULT_VALIDATOR = "final"

    def __init__(self, feed, validator=None, store_raw_records=False):
        """
        Constructs the validator.

        :param feed: String or file-like object representing the feed.
        :type feed: str or file
        """

        self._feed = None
        self._validator_name = validator if validator else self.DEFAULT_VALIDATOR

        #: :type: BaseValidator
        self._validator_instance = None
        self._result = None
        self._store_raw_records = store_raw_records

        if inspect.isclass(self._validator_name) and issubclass(self._validator_name, BaseValidator):
            self._validator = self._validator_name
            self._validator_name = self._validator.NAME
        elif isinstance(self._validator_name, str):
            self._validator = Registry.find(self._validator_name)
        else:
            raise ValueError(f"Validator {validator!r} is invalid.")

        if isinstance(feed, str):
            self._feed = io.StringIO(feed)
        elif is_file_like_object(feed):
            self._feed = feed
        else:
            raise ValueError("feed argument must either be a string or a file-like object.")

    def validate(self):
        """
        Validates feed.

        :returns: ValidatonResult object
        :rtype: ValidationResult
        """

        # Create validator instance...
        if self._validator_instance is None:
            self._validator_instance = self._validator(self._feed, store_raw_records=self._store_raw_records)
        if self._result is None:
            self._result = self._validator_instance.validate()
        return self._result

    @property
    def record_name(self):
        if self._validator_instance is not None:
            return self._validator_instance.RECORD_NAME
        return "???"

    @property
    def fields(self):
        return self._validator_instance.FIELDS if self._validator_instance else []

    def is_valid(self, allow_warnings=False):
        result = self.validate()
        return result.is_valid(allow_warnings=allow_warnings)
