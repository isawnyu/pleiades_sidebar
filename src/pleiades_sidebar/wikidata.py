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
import re
from textnorm import normalize_space, normalize_unicode
from urllib.parse import urlparse

DEFAULT_WIKIDATA_PATH = Path(environ["WIKIDATA_PATH"]).expanduser().resolve()

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
    def __init__(self, path: Path = DEFAULT_WIKIDATA_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "wikidata"
        if use_cache:
            Dataset.from_cache(self, namespace="wikidata")
        else:
            Dataset.load(self, path, "csv")

    def parse_all(self):
        logger = logging.getLogger("WikidataDataset.parse_all")
        for raw_item in self._raw_data:
            wikidata_item = WikidataDataItem(raw_item)
            try:
                self._data[wikidata_item.uri]
            except KeyError:
                self._data[wikidata_item.uri] = wikidata_item
            else:
                logger.debug(
                    f"Wikidata URI collision: {wikidata_item.uri}. Merging ..."
                )
                self._data[wikidata_item.uri].links["pleiades.stoa.org"].extend(
                    wikidata_item.links["pleiades.stoa.org"]
                )


class WikidataDataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse our standard wikipedia SPARQL result CSV into standard internal format"""

        logger = logging.getLogger("WikidataDataItem._parse")
        # label
        self.label = norm(self._raw_data["itemLabel"])

        # uri
        self.uri = norm(self._raw_data["item"])

        # summary
        # TBD

        # links
        links = set()
        for fieldname, resource_shortname in LINK_KEYS.items():
            if not resource_shortname:
                logger.debug(f"Skipping unsupported fieldname '{fieldname}'")
                continue
            try:
                val = self._raw_data[fieldname]
            except KeyError:
                logger.warning(f"Did not find expected fieldname '{fieldname}'")
                continue
            vals = [norm(s) for s in rx_delim.split(val)]
            vals = [s for s in vals if s != ""]
            try:
                base_uri = self._get_base_uri(resource_shortname)
            except NotImplementedError:
                continue
            if base_uri:
                links.update({base_uri + v for v in vals})
        dlinks = dict()
        for link in links:
            netloc = urlparse(link).netloc
            try:
                dlinks[netloc]
            except KeyError:
                dlinks[netloc] = list()
            dlinks[netloc].append(link)
        self.links = dlinks
