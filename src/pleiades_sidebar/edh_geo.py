#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from EDH GEO
"""
import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm
from urllib.parse import urlparse

DEFAULT_EDH_GEO_PATH = Path(environ["EDH_GEO_PATH"]).expanduser().resolve()


class EDHGEODataset(Dataset):
    def __init__(self, path: Path = DEFAULT_EDH_GEO_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "edhgeo"
        if use_cache:
            Dataset.from_cache(self, namespace=self.namespace)
        else:
            Dataset.load(self, path, "csv")

    def parse_all(self):
        logger = logging.getLogger("EDHGEODataset.parse_all")
        for raw_item in self._raw_data:
            item = EDHGEODataItem(raw_item)
            try:
                self._data[item.uri]
            except KeyError:
                self._data[item.uri] = item
            else:
                logger.debug(f"EDH GEO URI collision: {item.uri}. Merging ...")
                self._data[item.uri].links["pleiades.stoa.org"].extend(
                    item.links["pleiades.stoa.org"]
                )
        logger.info(
            f"Parsed {len(self._data):,} EDH GEO data items from {len(self._raw_data):,} raw data items."
        )


class EDHGEODataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse EDH GEO CSV data"""

        logger = logging.getLogger("EDHGEODataItem._parse")
        # label
        name = norm(self._raw_data["fo_antik"])
        if name:
            self.label = name
        else:
            self.label = norm(self._raw_data["fo_modern"])
        findspot = norm(self._raw_data["fundstelle"])
        if findspot:
            self.label += f" ({findspot})"

        # uri
        self.uri = self._get_base_uri("edhgeo") + norm(self._raw_data["id"])

        # summary
        # none

        # links
        links = dict()
        for k in [
            "pleiades_id_1",
            "pleiades_id_2",
            "geonames_id_1",
            "geonames_id_2",
            "trismegistos_geo_id",
        ]:
            this_id = norm(self._raw_data[k])
            if this_id:
                this_uri = self._get_base_uri(k.split("_")[0]) + this_id
                parts = urlparse(this_uri)
                domain = parts.netloc
                try:
                    links[domain]
                except KeyError:
                    links[domain] = list()
                links[domain].append(this_uri)
        self.links = links
