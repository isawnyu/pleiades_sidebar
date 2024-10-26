#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from Wikidata
"""
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pprint import pformat
import re
from textnorm import normalize_space, normalize_unicode

wikidata_path = Path(environ["WIKIDATA_PATH"]).expanduser().resolve()

LINK_KEYS = {
    "pleiades": "pleiades",
    "chronique_ids": "cfl/ado",
    "dare_ids": "dare",
    "geonames_ids": "geonames",
    "gettytgn_ids": "gettytgn",
    "idaigaz_ids": "idaigaz",
    "loc_ids": "loc",
    "manto_ids": "manto",
    "nomisma_ids": "nomisma",
    "topostext_ids": "topostext",
    "trismegistos_ids": "trismegistos",
    "viaf_ids": "viaf",
    "vici_ids": "vici",
    "wikipedia_en": "",
}
rx_delim = re.compile(r"(,|;)\s*")


def norm(s: str) -> str:
    return normalize_space(normalize_unicode(s))


class WikidataDataset(Dataset):
    def __init__(self):
        Dataset.__init__(self)
        Dataset.load(self, wikidata_path, "csv")

    def parse_all(self):
        for raw_item in self._raw_data:
            wikidata_item = WikidataDataItem(raw_item)


class WikidataDataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        # label
        self.label = norm(self._raw_data["itemLabel"])

        # uri
        self.uri = norm(self._raw_data["item"])

        # summary
        # TBD

        # links
        links = set()
        for fieldname, resource_shortname in LINK_KEYS.items():
            val = self._raw_data[fieldname]
            vals = [norm(s) for s in rx_delim.split(val)]
            vals = [s for s in vals if s != ""]
            base_uri = self._get_base_uri(resource_shortname)
            if base_uri:
                links.update({base_uri + v for v in vals})
        self.links = list(links)
