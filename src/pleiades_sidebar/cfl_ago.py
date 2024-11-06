#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from CFL/AGO
"""

import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm

DEFAULT_CFL_AGO_PATH = Path(environ["CFL_AGO_PATH"]).expanduser().resolve()


class CFLAGODataset(Dataset):
    def __init__(self, path: Path = DEFAULT_CFL_AGO_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "cflago"
        if use_cache:
            Dataset.from_cache(self, namespace=self.namespace)
        else:
            Dataset.load(self, path, "csv")

    def parse_all(self):
        logger = logging.getLogger("CFLAGODataset.parse_all")
        for raw_item in self._raw_data:
            item = CFLAGOataItem(raw_item)
            try:
                self._data[item.uri]
            except KeyError:
                self._data[item.uri] = item
            else:
                logger.debug(f"CFL/AGO URI collision: {item.uri}. Merging ...")
                self._data[item.uri].links["pleiades.stoa.org"].extend(
                    item.links["pleiades.stoa.org"]
                )


class CFLAGOataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse CFL/AGO CSV data"""

        logger = logging.getLogger("CFLAGODataItem._parse")

        # label
        self.label = norm(self._raw_data["Full_name"])

        # uri
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
