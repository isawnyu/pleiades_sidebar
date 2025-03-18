#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024-2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from Ancient Ports
"""

import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm
import re

DEFAULT_ANCIENT_PORTS_PATH = Path(environ["ANCIENT_PORTS_PATH"]).expanduser().resolve()


class AncientPortsDataset(Dataset):
    def __init__(self, path: Path = DEFAULT_ANCIENT_PORTS_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "ancient_ports"
        if use_cache:
            Dataset.from_cache(self, namespace=self.namespace)
        else:
            Dataset.load(self, path, "csv")

    def parse_all(self):
        logger = logging.getLogger("AncientPortsDataset.parse_all")
        for raw_item in self._raw_data:
            item = AncientPortsDataItem(raw_item)
            try:
                self._data[item.uri]
            except KeyError:
                self._data[item.uri] = item
            else:
                logger.debug(f"Ancient Ports URI collision: {item.uri}. Merging ...")
                self._data[item.uri].links["pleiades.stoa.org"].extend(
                    item.links["pleiades.stoa.org"]
                )


class AncientPortsDataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse Ancient Ports CSV data"""

        logger = logging.getLogger("AncientPortsDataItem._parse")

        # label
        name = norm(self._raw_data["NAME"])
        mod_name = norm(self._raw_data["NAME_MOD"])
        if name:
            self.label = name
        else:
            parts = [norm(p) for p in re.split(r"[\.,\?]") if norm(p)]
            if parts:
                self.label = parts[0]
                country = norm(self._raw_data["COUNTRY"])
                if country:
                    self.label += f", {country}"

        # uri
        # insufficient data in export to construct unique URIs
        # sent email 2025-03-18
        id = self._raw_data["Id"][len('GA_OPE_EDIT" target="_blank">') :].strip()
        self.uri = "https://chronique.efa.gr/?r=topo_public&id=" + id

        # summary
        self.summary = ""

        # links
        pid = self._raw_data["Pleiades_id"].strip()
        if pid:
            self.links = {
                "pleiades.stoa.org": [
                    (
                        "relatedMatch",
                        "https://pleiades.stoa.org/places/"
                        + self._raw_data["Pleiades_id"].strip(),
                    )
                ]
            }
