# SPDX-FileCopyrightText: 2022 2014 ANEXIA Internetdienstleistungs GmbH Authors: Stephan Peijnik <speijnik@anexia-it.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

Changelog
*********

next
----
* Announce support for python3.9
* Drop support for python < 3.6.2
* Introduce pre-commit, isort, black, lint with them and add github actions enforcing those styles
* Switch to poetry for dependency management and package building
* Use pytest for testing

0.6.1
-----
* Add changelog to packaged version
* Adjust long description for PyPi

0.6.0
-----
* Add support for latest pycountry (https://github.com/anexia-it/geofeed-validator/issues/4, thanks vangesseld)
* Add support for Python 3.5, 3.6, 3.7, 3.8, 3.9
* Drop support for Python 2
* Drop support for Python 3.2, 3.3, 3.4
* Update requirements to follow iso-codes 4.5.0
