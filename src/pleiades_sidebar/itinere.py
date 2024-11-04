#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from Itiner-e
"""
import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pprint import pformat
import re
from textnorm import normalize_space, normalize_unicode
from urllib.parse import urlparse

DEFAULT_ITINERE_PATH = Path(environ["ITINERE_PATH"]).expanduser().resolve()
rx_delim = re.compile(r"(,|;)\s*")


def norm(s: str) -> str:
    return normalize_space(normalize_unicode(s))


class ItinerEDataset(Dataset):
    def __init__(self, path: Path = DEFAULT_ITINERE_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "itinere"
        if use_cache:
            Dataset.from_cache(self, namespace="itinere")
        else:
            Dataset.load(self, path, "ndjson")

    def parse_all(self):
        logger = logging.getLogger("ItinerEDataset.parse_all")
        for raw_item in self._raw_data:
            itinere_item = ItinerEDataItem(raw_item)
            try:
                self._data[itinere_item.uri]
            except KeyError:
                self._data[itinere_item.uri] = itinere_item
            else:
                logger.debug(f"Itiner-E URI collision: {itinere_item.uri}. Merging ...")
                self._data[itinere_item.uri].links["pleiades.stoa.org"].extend(
                    itinere_item.links["pleiades.stoa.org"]
                )


class ItinerEDataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse the ItinerE ndjson export format"""

        # logger = logging.getLogger("ItinerEDataItem._parse")

        # label
        self.label = (
            f"{self._raw_data['id']} {norm(self._raw_data['properties']['name'])}"
        )

        # uri
        self.uri = self._get_base_uri("itinere") + str(self._raw_data["id"])

        # summary
        # none

        # links
        links = {p["properties"]["url"] for p in self._raw_data["pleiadesPlaces"]}
        self.links = {"pleiades.stoa.org": [("relatedMatch", link) for link in links]}
