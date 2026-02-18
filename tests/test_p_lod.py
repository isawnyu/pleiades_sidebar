#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2026 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the p-lod.github.io dataset"""

import logging
from pleiades_sidebar.p_lod import PLODDataset

logger = logging.getLogger(__name__)


class TestPLODDataset:
    def test__init(self):
        dataset = PLODDataset(use_cache=False)
        assert dataset.namespace == "p_lod"
        assert dataset._raw_data is not None
        assert dataset._data is not None
