#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a base class for a dataset manager
"""
from encoded_csv import get_csv
import logging
from pathlib import Path
from pprint import pformat


class DataItem:
    """An individual data item in a dataset"""

    def __init__(self, raw: dict):
        self.label = None
        self.uri = None
        self.summary = None
        self.links = dict()
        self._raw_data = raw
        # TBD: make spatial?
        self._parse()

    def _parse(self):
        """Parse/ingest the raw data for this item into label, uri, and summary fields
        OVERLOAD THIS METHOD for each dataset"""
        # make sure you populate
        # label
        # uri
        # summary
        # links
        pass


class Dataset:
    """Base class for a dataset manager"""

    def __init__(self):
        self._data = dict()  # Parsed DataItems keyed by URI
        # Dictionary of lists of DataItem IDs keyed by Pleiades URIs
        self._pleiades_index = dict()

    def get(self, item_uri: str) -> DataItem:
        """Get a parsed dataitem by its URI"""
        try:
            return self._data[item_uri]
        except KeyError:
            return None

    def get_pleiades(self, pleiades_uri: str) -> list:
        """Return a list of IDs for all items in this dataset that correspond to a Pleiades URI"""
        try:
            return self._pleiades_index[pleiades_uri]
        except KeyError:
            return list()

    def load(self, datafile_path: Path, load_method: str):
        """Load the target dataset"""
        cmd = f"_load_{load_method}"
        getattr(self, cmd)(datafile_path)
        self.parse_all()

    def parse_all(self):
        """Parse the already-loaded dataset"""
        # OVERRIDE THIS METHOD FOR EACH DATASET
        pass

    def _load_csv(self, datafile_path: Path):
        data = get_csv(str(datafile_path), sample_lines=1000)
        logger = logging.getLogger("_load_csv")
        logger.debug(
            f"Loaded {len(data['content'])} rows of data with fieldnames: {pformat(data['fieldnames'], indent=4)}"
        )
        self._raw_data = data["content"]
