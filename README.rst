# SPDX-FileCopyrightText: 2022 2014 ANEXIA Internetdienstleistungs GmbH Authors: Stephan Peijnik <speijnik@anexia-it.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

=================
geofeed-validator
=================
.. image:: https://github.com/anexia-it/geofeed-validator/actions/workflows/python-package.yml/badge.svg?branch=master
	:target: https://github.com/anexia-it/geofeed-validator/actions/workflows/python-package.yml/badge.svg?branch=master

.. image:: https://coveralls.io/repos/anexia-it/geofeed-validator/badge.png?branch=master
	:target: https://coveralls.io/r/anexia-it/geofeed-validator?branch=master

.. image:: https://img.shields.io/pypi/dm/geofeed_validator.svg
        :target: https://pypi.python.org/pypi/geofeed_validator/

.. image:: https://img.shields.io/pypi/v/geofeed_validator.svg
        :target: https://pypi.python.org/pypi/geofeed_validator/

.. image:: https://img.shields.io/pypi/wheel/geofeed_validator.svg
        :target: https://pypi.python.org/pypi/geofeed_validator/

.. image:: https://img.shields.io/pypi/l/geofeed_validator.svg
        :target: https://pypi.python.org/pypi/geofeed_validator/


geofeed-validator is a Python library which implements validation for self-published geofeeds as defined in
http://tools.ietf.org/html/draft-google-self-published-geofeeds-02.

Additionally to the library a sample CLI application is provided, which allows to validate geolocation feeds,
either located in the local filesystem, or downloaded from a remote host using urllib2.
