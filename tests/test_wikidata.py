#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the Wikidata module 
"""

from pleiades_sidebar.wikidata import WikidataDataset
import pytest

# test_wikidata.py


def test_wikidata_dataset_initialization():
    # Create an instance of WikidataDataset
    wikidata_dataset = WikidataDataset()

    # Check if the instance is created successfully
    assert isinstance(wikidata_dataset, WikidataDataset)
