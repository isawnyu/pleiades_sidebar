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
from urllib.parse import urlparse

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
                raise NotImplementedError(f"WHG URI collision: {item.uri}. Merging ...")


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
        self.uri = norm(str(props["pid"]))

        # links
        ld_context = self._raw_data.get("@context", {})
        links = [
            link["identifier"].split(":")
            for link in self._raw_data.get("links", [])
            if link["type"] == "closeMatch"
        ]
        self.links = dict()
        for link in links:
            ns, link_id = link
            try:
                base_uri = ld_context[ns]
            except KeyError:
                if ns == "pl":
                    base_uri = "https://pleiades.stoa.org/places/"
                else:
                    raise NotImplementedError(
                        f"Unknown namespace abbreviation '{ns}' in WHG links"
                    )
            full_uri = f"{base_uri}{link_id}"
            netloc = urlparse(full_uri).netloc
            try:
                self.links[netloc]
            except KeyError:
                self.links[netloc] = list()
            self.links[netloc].append(("relatedMatch", full_uri))
