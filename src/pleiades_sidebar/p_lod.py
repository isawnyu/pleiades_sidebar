#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024-2026 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from p-lod.github.io
"""

import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm
from pprint import pformat

DEFAULT_PLOD_PATH = Path(environ["P_LOD_PATH"]).expanduser().resolve()


class PLODDataset(Dataset):
    def __init__(self, path: Path = DEFAULT_PLOD_PATH, use_cache=False):

        logger = logging.getLogger("PLODDataset.__init__")
        logger.debug(
            f"Initializing PLODDataset with path {path} and use_cache={use_cache}"
        )
        Dataset.__init__(self)
        self.namespace = "p_lod"
        if use_cache:
            Dataset.from_cache(self, namespace=self.namespace)
        else:
            Dataset.load(self, path, "csv")

    def parse_all(self):
        logger = logging.getLogger("PLODDataset.parse_all")
        for raw_item in self._raw_data:
            item = PLODDataItem(raw_item)
            try:
                self._data[item.uri]
            except KeyError:
                self._data[item.uri] = item
            else:
                logger.debug(f"PLOD URI collision: {item.uri}. Merging ...")
                self._data[item.uri].links["pleiades.stoa.org"].extend(
                    item.links["pleiades.stoa.org"]
                )


class PLODDataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse p-lod.github.io CSV data"""

        logger = logging.getLogger("PLODDataItem._parse")

        # label
        self.label = norm(self._raw_data["label"])

        # uri
        url = norm(self._raw_data["url"])
        self.uri = url

        # summary
        english_title = norm(self._raw_data["plod-english-title"])
        italian_title = norm(self._raw_data["plod-italian-title"])
        description = norm(self._raw_data["description"])
        if english_title:
            self.summary = english_title
        elif italian_title:
            self.summary = italian_title
        elif description:
            self.summary = description
        else:
            self.summary = ""

        # links
        self.links = {}
        pid = norm(self._raw_data["pleiades-url"])
        if pid:
            self.links["pleiades.stoa.org"] = [
                ("relatedMatch", f"https://pleiades.stoa.org/places/{pid}")
            ]
        pinp_url = norm(self._raw_data["p-in-p-url"])
        if pinp_url:
            self.links["pompeiiinpictures.com"] = [("relatedMatch", pinp_url)]
