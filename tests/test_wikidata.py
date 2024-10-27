#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the Wikidata module 
"""

from pathlib import Path
from pleiades_sidebar.wikidata import WikidataDataset, WikidataDataItem
import pytest

# test_wikidata.py

TEST_DATA_DIR = Path("tests/data/")


class TestWikidataDataset:

    @classmethod
    def setup_class(cls):
        # Create an instance of WikidataDataset
        cls.wikidata_dataset = WikidataDataset(
            wikidata_path=TEST_DATA_DIR / "wikidata.csv"
        )

    def test_wikidata_dataset_initialization(self):

        # Check if the instance is created successfully
        assert isinstance(self.wikidata_dataset, WikidataDataset)

    def test_wikidata_dataset_load(self):
        """Did we load the expected number of items"""
        assert len(self.wikidata_dataset) == 11

    def test_wikidata_dataset_pleiades_indexing(self):
        """Did we index the expected number of Pleiades IDs"""
        assert len(self.wikidata_dataset._pleiades_index) == 11


def test_wikidata_dataitem_initialization():
    d = {
        "pleiades": "266040",
        "item": "http://www.wikidata.org/entity/Q5685282",
        "itemLabel": "Sierra Elvira",
    }
    wikidata_dataitem = WikidataDataItem(d)
    assert isinstance(wikidata_dataitem, WikidataDataItem)
    assert wikidata_dataitem.label == "Sierra Elvira"
    assert wikidata_dataitem.pleiades_uris == [
        "https://pleiades.stoa.org/places/266040"
    ]
    assert wikidata_dataitem.uri == "http://www.wikidata.org/entity/Q5685282"
