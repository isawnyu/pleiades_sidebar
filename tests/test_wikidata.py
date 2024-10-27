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

    def test_wikidata_dataset_lpf(self):
        """Do we get an LPF feature collection?"""
        assert len(self.wikidata_dataset.to_lpf_dict()["features"]) == 11

    def test_wikidata_dataset_from_cache(self):
        """Can we get the data from cache?"""
        wd = WikidataDataset(use_cache=True)
        assert len(wd) == 11


class TestWikidataDataItem:

    @classmethod
    def setup_class(cls):
        d = {
            "pleiades": "266040",
            "item": "http://www.wikidata.org/entity/Q5685282",
            "itemLabel": "Sierra Elvira",
        }
        cls.wikidata_dataitem = WikidataDataItem(d)

    def test_wikidata_dataitem_initialization(self):
        """Did we successfully create a Wikidata DataItem?"""
        assert isinstance(self.wikidata_dataitem, WikidataDataItem)

    def test_wikidata_dataitem_label(self):
        """Did we successfully parse and store the proper label?"""
        assert self.wikidata_dataitem.label == "Sierra Elvira"

    def test_wikidata_dataitem_pleiades(self):
        """Did we successfully parse and store the corresponding Pleiades URI?"""
        assert self.wikidata_dataitem.pleiades_uris == [
            "https://pleiades.stoa.org/places/266040"
        ]

    def test_wikidata_dataitem_uri(self):
        """Did we successfully parse and store the Wikidata Entity URI?"""
        assert self.wikidata_dataitem.uri == "http://www.wikidata.org/entity/Q5685282"

    def test_wikidata_dataitem_lpf(self):
        """Do we get expected LPF dictionary for this Wikidata Entity?"""
        assert self.wikidata_dataitem.to_lpf_dict() == {
            "@id": "http://www.wikidata.org/entity/Q5685282",
            "type": "Feature",
            "properties": {"title": "Sierra Elvira", "summary": None},
            "links": [
                {
                    "type": "closeMatch",
                    "identifier": "https://pleiades.stoa.org/places/266040",
                }
            ],
        }
