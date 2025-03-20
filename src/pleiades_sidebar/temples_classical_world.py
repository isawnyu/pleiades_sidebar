#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024-2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from Temples of the Classical World
"""

import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm

DEFAULT_CLASSICAL_TEMPLES_PATH = (
    Path(environ["CLASSICAL_TEMPLES_PATH"]).expanduser().resolve()
)


class ClassicalTemplesDataset(Dataset):
    def __init__(self, path: Path = DEFAULT_CLASSICAL_TEMPLES_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "classical_temples"
        if use_cache:
            Dataset.from_cache(self, namespace=self.namespace)
        else:
            Dataset.load(self, path, "csv")

    def parse_all(self):
        logger = logging.getLogger("ClassicalTemplesDataset.parse_all")
        for raw_item in self._raw_data:
            item = ClassicalTemplesDataItem(raw_item)
            try:
                self._data[item.uri]
            except KeyError:
                self._data[item.uri] = item
            else:
                logger.debug(
                    f"Classical Temples URI collision: {item.uri}. Merging ..."
                )
                self._data[item.uri].links["pleiades.stoa.org"].extend(
                    item.links["pleiades.stoa.org"]
                )


class ClassicalTemplesDataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse Classical Temples CSV data"""

        logger = logging.getLogger("ClassicalTemplesDataItem._parse")

        # label
        self.label = norm(self._raw_data["name"])

        # uri
        id = norm(self._raw_data["id"])
        self.uri = f"https://romeresearchgroup.org/items/{id}"

        # summary
        location = norm(self._raw_data["location"])
        modern_place = norm(self._raw_data["modernplace"])
        if location and modern_place:
            self.summary = f"{location}, {modern_place}"
        elif location:
            self.summary = f"{location}"
        elif modern_place:
            self.summary = modern_place
        self.summary = ""

        # links
        pid = norm(self._raw_data["pleiades"])
        if pid:
            self.links = {
                "pleiades.stoa.org": [
                    ("relatedMatch", f"https://pleiades.stoa.org/places/{pid}")
                ]
            }
