# geofeed_validator/validator/base.py
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

import cStringIO
import inspect

import six

from geofeed_validator.fields import Field, NetworkField, CountryField, SubdivisionField, CityField, ZipCodeField
from geofeed_validator.utils import is_file_like_object
from geofeed_validator.result import ValidationResult


class BaseValidator(object):
    '''
    Base validator functionality.
    '''
    NAME = None
    FIELDS = None
    RECORD_NAME = 'record'

    def __init__(self, feed, store_raw_records=False):
        if not isinstance(getattr(self, 'NAME', None), six.string_types):
            raise ValueError('NAME class-attribute of %r not set or invalid (type=%r).'
                             % (self.__class__, type(getattr(self, 'NAME', None))))

        if type(getattr(self, 'FIELDS', None)) not in (list, tuple):
            raise ValueError('FIELDS class-attribute of %r not set or invalid (type=%r).'
                             % (self.__class__, type(getattr(self, 'FIELDS', None))))

        self._fields = list()
        for field_or_class in getattr(self, 'FIELDS'):
            if not isinstance(field_or_class, Field) and inspect.isclass(field_or_class) and issubclass(field_or_class, Field):
                field_or_class = field_or_class()
            elif not isinstance(field_or_class, Field):
                raise ValueError('FIELDS class %r not subclass/instance of %r.' % (field_or_class, Field))

            self._fields.append(field_or_class)

        self._feed = None
        self._store_raw_records = store_raw_records
        if isinstance(feed, six.string_types):
            self._feed = cStringIO.StringIO(feed)
        elif is_file_like_object(feed):
            self._feed = feed
        else:
            raise ValueError('feed argument must either be a string or a file-like object.')

    def get_records(self):
        raise NotImplementedError

    def validate(self):
        '''
        Validates the feed in self._feed.
        :returns: ValidationResult object
        :rtype: ValidationResult
        '''
        result = ValidationResult(self._fields, self._store_raw_records)
        for record, raw_data in self.get_records():
            result.add_record(record, raw_data)

        self._validate_common(result)
        return result

    def _validate_common_network_duplicates(self, networks, record):
        network = record.get_field_result(NetworkField)

        if network:
            network_str = str(network.value)
            if network_str in networks.keys():
                for other_network_record in networks[network_str]:
                    other_network_record.add_field_errors(NetworkField, 'Duplicate of %s #%d' % (self.RECORD_NAME,
                                                                                                 record.record_no))
                    record.add_field_errors(NetworkField, 'Duplicate of %s #%d' % (self.RECORD_NAME,
                                                                                   other_network_record.record_no))
                networks[network_str].append(record)
            else:
                networks[network_str] = [record,]
        return networks

    def _validate_common_geoinfo(self, record):
        country = record.get_field_value(CountryField)
        subdivision = record.get_field_value(SubdivisionField)
        city = record.get_field_value(CityField)
        zipcode = record.get_field_value(ZipCodeField)

        if country and subdivision and subdivision.country != country:
            record.add_field_errors(SubdivisionField, 'Subdivision not a subdivison of given country.')

        elif subdivision and not country:
            record.add_field_errors(SubdivisionField, 'Subdivision specified, but country missing/invalid.')

        if city and not country:
            record.add_field_errors(CityField, 'City specified, but country missing/invalid.')

        if zipcode and not country:
            record.add_field_errors(ZipCodeField, 'Zipcode specified, but country missing/invalid.')

    def _validate_common_extra(self, record):
        pass

    def _validate_common(self, result):
        '''
        :type: result list of RecordValidationResult
        '''
        networks = dict()

        for record in result.records:
            # Check for duplicate network entries
            networks = self._validate_common_network_duplicates(networks, record)

            # Validate country, division, city, zipcode
            self._validate_common_geoinfo(record)

            # Extra validations...
            self._validate_common_extra(record)


class BaseCSVValidator(BaseValidator):
    RECORD_NAME = 'line'

    '''
    Base implementation for CSV validator
    '''
    def get_records(self):
        '''
        Processes CSV contents on a per-line basis
        '''
        for line in self._feed.readlines():
            # Process one line at a time...
            line = line.strip()
            if line == '' or line.startswith('#'):
                # Empty line/comment
                yield {}, line
                continue

            field_values = line.split(',')
            record = dict(zip(self._fields, field_values))
            if len(field_values) > len(self._fields):
                record.update({
                    '__extra__': field_values[len(self._fields):]
                })

            yield record, line


class Registry(object):
    '''
    Validator registry
    '''
    VALIDATORS = dict()

    @classmethod
    def register(cls, validator_class):
        if not inspect.isclass(validator_class) or not issubclass(validator_class, BaseValidator):
            raise ValueError('%r is not a subclass of BaseValidator.' % validator_class)

        if not isinstance(getattr(validator_class, 'NAME', None), six.string_types):
            raise ValueError('NAME class-attribute missing from %r.' % validator_class)

        cls.VALIDATORS[getattr(validator_class, 'NAME')] = validator_class

    @classmethod
    def find(cls, name):
        if not name in cls.VALIDATORS.keys():
            raise KeyError('Validator with name %r not registered.' % name)
        return cls.VALIDATORS[name]

    @classmethod
    def names(cls):
        return cls.VALIDATORS.keys()

