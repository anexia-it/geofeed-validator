# Copyright (C) 2014 ANEXIA Internetdienstleistungs GmbH
# SPDX-FileCopyrightText: 2022 2014 ANEXIA Internetdienstleistungs GmbH Authors: Stephan Peijnik <speijnik@anexia-it.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from geofeed_validator.fields import Field


class AllocationSizeField(Field):
    ERROR = "Must be valid CIDR notation"
    NAME = "allocation_size"

    def _check_errors(self, value):
        try:
            self.to_python(value)
        except Exception as e:
            return True
        return False

    def to_python(self, value):
        if value and not value.startswith("/"):
            raise ValueError("Value does not start with a slash")
        elif value:
            return int(value[1:])
        else:
            return ""
