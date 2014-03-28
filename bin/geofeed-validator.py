#!/usr/bin/env python
#
# bin/geofeed_validator.py
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

import argparse
import sys
import os
import traceback

from geofeed_validator import GeoFeedValidator, __version__, Registry

QUIET = False


def write_console(fmt, *args, **kwargs):
    global QUIET

    if QUIET:
        return

    fmt = fmt % args
    fmt = fmt % kwargs
    sys.stdout.write(fmt)
    sys.stdout.flush()


def write_console_line(fmt, *args, **kwargs):
    write_console(fmt + '\n', *args, **kwargs)


def validate(fp, verbose=False, validator_name=None, allow_warnings=False):
    try:
        validator_class = Registry.find(validator_name)
    except KeyError:
        sys.stderr.write('Validator %s not found.' % validator_name)
        return 4

    val = GeoFeedValidator(fp, validator=validator_class, store_raw_records=True)
    write_console('Validating feed: ')
    result = val.validate()
    write_console_line('DONE.')

    records_with_warnings = 0
    records_with_errors = 0
    for record in result.records:
        line_status = 'OK'
        if record.has_errors or record.has_warnings:
            line_status = '%s%s' % ('E' if record.has_errors else ' ',
                                    'W' if record.has_warnings else ' ')

            if record.has_errors:
                records_with_errors += 1
            if records_with_warnings:
                records_with_warnings += 1

        if verbose or record.has_errors or record.has_warnings:
            write_console_line('[%s %d %s] %s', val.record_name, record.record_no, line_status, record.raw)

        for field_result in record.field_results:
            for err_string in field_result.errors:
                write_console_line('  E %s - %s', field_result.field.name, err_string)
            for warn_string in field_result.warnings:
                write_console_line('  W %s - %s', field_result.field.name, warn_string)

    write_console_line('%s%ss: %d TOTAL, %d VALID, %d ERROR, %d WARNING', val.record_name[0].upper(),
                       val.record_name[1:], len(result.records), len(result.records)-records_with_errors,
                       records_with_errors, records_with_warnings)
    write_console_line('Counts: %d ERROR%s, %d WARNING%s',
                       result.error_count, 's' if result.error_count != 1 else '',
                       result.warning_count, 's' if result.warning_count != 1 else '')

    if val.is_valid(allow_warnings=allow_warnings):
        write_console_line('*** Feed VALID ***')
        return 0
    write_console_line('*** Feed INVALID ***')
    return 3



def main(argv=sys.argv):
    global QUIET

    parser = argparse.ArgumentParser(prog=argv[0])
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true', default=False)
    parser.add_argument('-V', '--version', help='Print version and exit.', action='store_true', default=False)
    parser.add_argument('-t', '--typ', help='Validator type', choices=Registry.names(), default='draft02')
    parser.add_argument('-q', '--quiet', help='Suppress all output', action='store_true', default=False)
    parser.add_argument('-w', '--warnings', help='Treat warnings as errors', action='store_true', default=False)
    parser.add_argument('source', type=str, help='URL or path to feed file')

    args = parser.parse_args(argv[1:])

    QUIET = args.quiet
    if args.version:
        QUIET = False

    version_header()
    if args.version:
        return 0

    fp = None
    if os.path.exists(args.source):
        try:
            fp = open(args.source, 'r')
        except IOError, e:
            sys.stderr.write('*** ERROR: Could not read %s: %s\n' % (args.source, e))
            return 2

    else:
        import urllib2
        try:
            write_console('*** Fetching %s: ', args.source)
            fp = urllib2.urlopen(args.source, timeout=3)
            write_console_line('DONE.')
        except Exception, e:
            write_console_line('FAILED.')
            sys.stderr.write('*** ERROR: Could not open URL %s: %s\n' % (args.source, e))
            return 2

    try:
        result = validate(fp, verbose=args.verbose, validator_name=args.typ, allow_warnings=not args.warnings)
        try:
            fp.close()
        except:
            pass
        return result
    except:
        sys.stderr.write('\n\n*** GeoFeedValidator has encountered an internal error.\n')
        sys.stderr.write('*** This is most likely related to a bug.\n')
        sys.stderr.write('*** Please report this bug, including the traceback below to speijnik(at)anexia-it.com\n')
        sys.stderr.write('*** TRACEBACK: %s' % traceback.format_exc())
        return 255


def version_header():
    write_console_line('*** ANEXIA GeoFeed Validator v%s' % __version__)

if __name__ == '__main__':
    sys.exit(main())




