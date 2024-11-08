#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Normalize text
"""

from textnorm import normalize_space, normalize_unicode


def norm(s: str) -> str:
    """Normalize space and unicode"""
    return normalize_space(normalize_unicode(s))
