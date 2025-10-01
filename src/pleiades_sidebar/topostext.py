#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024-2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from ToposText
"""

import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm

DEFAULT_TOPOSTEXT_PATH = Path(environ["TOPOSTEXT_PATH"]).expanduser().resolve()


class ToposTextDataset(Dataset):
    def __init__(self, path: Path = DEFAULT_TOPOSTEXT_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "topostext"
        if use_cache:
            Dataset.from_cache(self, namespace=self.namespace)
        else:
            Dataset.load(self, path, "csv")

    def parse_all(self):
        logger = logging.getLogger("ToposTextDataset.parse_all")
        for raw_item in self._raw_data:
            item = ToposTextDataItem(raw_item)
            try:
                self._data[item.uri]
            except KeyError:
                self._data[item.uri] = item
            else:
                logger.debug(f"ToposText URI collision: {item.uri}. Merging ...")
                self._data[item.uri].links["pleiades.stoa.org"].extend(
                    item.links["pleiades.stoa.org"]
                )


class ToposTextDataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse ToposText CSV data"""

        logger = logging.getLogger("ToposTextDataItem._parse")

        # label
        self.label = norm(self._raw_data["TITLE"])

        # uri
        id = norm(self._raw_data["TTID"])
        self.uri = f"https://topostext.org/place/{id}"

        # summary
        summary = norm(self._raw_data["SHORTDESC"])
        self.summary = summary

        # links
        pid = norm(self._raw_data["PLEIADES"])
        if pid:
            self.links = {
                "pleiades.stoa.org": [
                    ("relatedMatch", f"https://pleiades.stoa.org/places/{pid}")
                ]
            }
