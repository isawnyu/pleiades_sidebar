#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from Wikidata
"""
import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pprint import pformat
from textnorm import normalize_space, normalize_unicode

logger = logging.getLogger("pleiades_sidebar")
wikidata_path = Path(environ["WIKIDATA_PATH"]).expanduser().resolve()
logger.debug(f"Wikidata path: {wikidata_path}")


def norm(s: str) -> str:
    return normalize_space(normalize_unicode(s))


class WikidataDataset(Dataset):
    def __init__(self):
        Dataset.__init__(self)
        Dataset.load(self, wikidata_path, "csv")

    def parse_all(self):
        for raw_item in self._raw_data:
            wikidata_item = WikidataDataItem(raw_item)
            logger.debug(pformat(wikidata_item, indent=4))
            exit()


class WikidataDataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        self.label = norm(self._raw_data["itemLabel"])
        self.uri = norm(self._raw_data["item"])
        # label
        # uri
        # summary
        # links
