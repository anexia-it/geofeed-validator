# geofeed_validator/validation.py
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
import inspect

import six

from geofeed_validator.fields import Field


class FieldResult(object):
    def __init__(self, field, value, errors, warnings, raw, value_string):
        self.field = field
        self.value = value
        self.errors = errors
        self.warnings = warnings
        self.raw = raw
        self.value_string = value_string

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['value']
        return state

    def __setstate__(self, state):
        field = state['field']
        value = None
        if state.get('value_string', None):
            try:
                value = field.to_python(state['value_string'])
            except:
                pass

        state['value'] = value
        self.__dict__.update(state)


class RecordValidationResult(object):
    '''
    Validation result for a single record
    '''
    def __init__(self, record_no, fields, record, raw_data):
        '''
        :param record_no: Record number
        :type record_no: int
        :param fields: List of fields as defined by the validator
        :type fields: list of Field
        :param record: File to value mapping
        :type record: dict of (Field, str)
        :param raw_data: Raw record data, as read by parser
        :type raw_data: basestring
        '''
        self._record_no = record_no
        self._fields = fields
        self._record = record
        self._raw_data = raw_data
        self._was_ignored = False

        #: :type: bool
        self._has_extra = record.has_key('__extra__')
        #: :type: list of str
        self._extra = list()
        self._extra_offset = 0
        #: :type: list of FieldResult
        self._field_results = list()

        if self._has_extra:
            self._extra = record['__extra__']
            del record['__extra__']
            self._extra_offset = len(record)

    @property
    def field_results(self):
        return self._field_results

    def validate(self):
        if len(self._record) == 0:
            self._was_ignored = True
            return

        for field in self._fields:
            if not field in self._record.keys():
                self._field_results.append(FieldResult(field, None, ['Field is missing.'], [], None, ''))
            else:
                # Validate the field data...
                errors, warnings, cleaned_value = field.validate(self._record[field])
                self._field_results.append(FieldResult(field, cleaned_value, list(errors), list(warnings),
                                                       self._record[field], field.to_string(self._record[field])))

    def add_field_errors(self, field, errors):
        if type(errors) == tuple:
            errors = list(errors)
        elif type(errors) != list:
            errors = [errors,]

        field_result = self.get_field_result(field)
        if field_result:
            field_result.errors += errors
            return

        self._field_results.append(FieldResult(field, None, errors, [], None, ''))

    def add_field_warnings(self, field, warnings):
        if type(warnings) == tuple:
            warnings = list(warnings)
        elif type(warnings) != list:
            warnings = [warnings,]

        field_result = self.get_field_result(field)
        if field_result:
            field_result.warnings += warnings
            return

        self._field_results.append(FieldResult(field, None, [], warnings, None, ''))

    def get_field_result(self, field_name_or_class):
        '''
        :param field_name_or_class: Field name or class
        :type field_name_or_class: str or Field
        :returns: FieldResult instance if found, None otherwise.
        :rtype: FieldResult
        '''
        field_name = field_name_or_class
        if inspect.isclass(field_name_or_class) and issubclass(field_name_or_class, Field):
            field_name = field_name_or_class.NAME
        elif isinstance(field_name_or_class, Field):
            field_name = field_name_or_class.name

        for fr in self._field_results:
            if fr.field.name == field_name:
                return fr
        return None

    def get_field_value(self, field_name_or_class):
        field_result = self.get_field_result(field_name_or_class)
        if field_result:
            return field_result.value
        return None

    @property
    def raw(self):
        return self._raw_data

    @property
    def extra_offset(self):
        return self._extra_offset

    @property
    def extra(self):
        return self._extra

    @property
    def error_count(self):
        return sum(map(lambda fr: len(fr.errors), self._field_results))

    @property
    def warning_count(self):
        return sum(map(lambda fr: len(fr.warnings), self._field_results))

    @property
    def has_errors(self):
        return self.error_count > 0

    @property
    def has_warnings(self):
        return self.warning_count > 0

    @property
    def record_no(self):
        return self._record_no

    @property
    def was_ignored(self):
        return self._was_ignored


class ValidationResult(object):
    '''
    Class representing a validation result.
    '''

    def __init__(self, fields, store_raw_records=False):
        #: :type: list of RecordValidationResult
        self._records = list()
        self._store_raw_records = store_raw_records
        self._fields = fields

    def add_record(self, record, raw_data):
        '''
        :param record: Record data as dict
        :type record: dict of (Field, value)
        '''
        if not self._store_raw_records:
            raw_data = None

        record_no = len(self._records)
        record_validation = RecordValidationResult(record_no, self._fields, record, raw_data)
        record_validation.validate()
        self._records.append(record_validation)

    @property
    def records_raw(self):
        if not self._store_raw_records:
            return list()

        # TODO: this seems to be broken if the number of records is one.
        return list(map(lambda r: r.raw, self._records))

    @property
    def fields(self):
        return self._fields

    @property
    def error_count(self):
        return sum(map(lambda r: r.error_count, self._records))

    @property
    def warning_count(self):
        return sum(map(lambda r: r.warning_count, self._records))

    @property
    def records(self):
        return self._records

    def is_valid(self, allow_warnings=False):
        if allow_warnings:
            return self.error_count == 0
        return self.error_count == 0 and self.warning_count == 0