#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from MANTO
"""
import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm

DEFAULT_MANTO_PATH = Path(environ["MANTO_PATH"]).expanduser().resolve()


class MANTODataset(Dataset):
    def __init__(self, path: Path = DEFAULT_MANTO_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "manto"
        if use_cache:
            Dataset.from_cache(self, namespace="manto")
        else:
            Dataset.load(self, path, "csv")

    def parse_all(self):
        logger = logging.getLogger("MANTODataset.parse_all")
        for raw_item in self._raw_data:
            item = MANTODataItem(raw_item)
            try:
                self._data[item.uri]
            except KeyError:
                self._data[item.uri] = item
            else:
                logger.debug(f"MANTO URI collision: {item.uri}. Merging ...")
                self._data[item.uri].links["pleiades.stoa.org"].extend(
                    item.links["pleiades.stoa.org"]
                )


class MANTODataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse MANTO CSV data"""

        logger = logging.getLogger("MANTODataItem._parse")
        # label
        self.label = norm(self._raw_data["Name"])

        # uri
        self.uri = " https://resource.manto.unh.edu/" + norm(
            self._raw_data["Object ID"]
        )

        # summary
        self.summary = norm(self._raw_data["Information"])
        if self.summary:
            self.summary = self.summary[0].upper() + self.summary[1:]

        # links
        self.links = {
            "pleiades.stoa.org": [
                (
                    "relatedMatch",
                    "https://pleiades.stoa.org/places/" + self._raw_data["Pleiades"],
                )
            ]
        }
