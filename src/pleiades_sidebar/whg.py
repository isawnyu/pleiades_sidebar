#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024-2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from World Historical Gazetteer (WHG)
"""

import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm

DEFAULT_WHG_PATH = Path(environ["WHG_PATH"]).expanduser().resolve()


class WHGDataset(Dataset):
    def __init__(self, path: Path = DEFAULT_WHG_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "whg"
        if use_cache:
            Dataset.from_cache(self, namespace=self.namespace)
        else:
            Dataset.load(self, path, "json")

    def parse_all(self):
        logger = logging.getLogger("WHGDataset.parse_all")
        for raw_item in self._raw_data.get("features", []):
            item = WHGDataItem(raw_item)
            try:
                self._data[item.uri]
            except KeyError:
                self._data[item.uri] = item
            else:
                logger.debug(f"WHG URI collision: {item.uri}. Merging ...")
                # You may want to merge links or other properties here


class WHGDataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse a WHG GeoJSON feature"""

        logger = logging.getLogger("WHGDataItem._parse")

        props = self._raw_data.get("properties", {})

        # label
        self.label = norm(props.get("title", ""))

        # uri
        self.uri = norm(props.get("pid", "")) or norm(props.get("id", ""))

        # summary
        self.summary = norm(props.get("description", ""))

        # links
        pleiades_id = props.get("pleiades_id", "")
        if pleiades_id:
            self.links = {
                "pleiades.stoa.org": [
                    ("relatedMatch", f"https://pleiades.stoa.org/places/{pleiades_id}")
                ]
            }
        else:
            self.links = {}
