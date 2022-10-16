# Copyright (C) 2014 ANEXIA Internetdienstleistungs GmbH
# SPDX-FileCopyrightText: 2022 2014 ANEXIA Internetdienstleistungs GmbH Authors: Stephan Peijnik <speijnik@anexia-it.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

def is_file_like_object(obj):
    """
    Helper function that checks if a given object is a file-like object.

    :param obj: Object to check
    :type obj: object
    :returns: True if obj is file-like, False otherwise
    :rtype: bool
    """
    return hasattr(obj, "read") and hasattr(obj, "close")
