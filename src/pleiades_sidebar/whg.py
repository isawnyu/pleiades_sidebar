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
from pprint import pformat
from urllib.parse import urlparse

DEFAULT_WHG_PATH = Path(environ.get("WHG_PATH", "")).expanduser().resolve()


class WHGDataset(Dataset):
    def __init__(self, path: Path = DEFAULT_WHG_PATH, use_cache=False, **kwargs):
        Dataset.__init__(self, **kwargs)
        self.namespace = "whg"
        if use_cache:
            Dataset.from_cache(self, namespace=self.namespace)
        else:
            Dataset.load(self, path, "jsonlpf")

    def parse_all(self):
        logger = logging.getLogger("WHGDataset.parse_all")
        for raw_item in self._raw_data:
            item = WHGDataItem(raw_item, self._context)
            try:
                self._data[item.uri]
            except KeyError:
                self._data[item.uri] = item
            else:
                raise NotImplementedError(f"WHG URI collision: {item.uri}. Merging ...")


class WHGDataItem(DataItem):
    def __init__(self, raw: dict, context: dict):
        self._context = context
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse a WHG GeoJSON feature"""

        logger = logging.getLogger("WHGDataItem._parse")

        props = self._raw_data.get("properties", {})

        # label
        self.label = norm(props.get("title", ""))

        # uri
        self.uri = (
            self._get_base_uri("whg") + norm(str(props["pid"])) + "/detail"
        )  # sic

        # links
        links = [
            link["identifier"].split(":")
            for link in self._raw_data.get("links", [])
            if link["type"] == "closeMatch"
        ]

        self.links = dict()
        for link in links:
            try:
                ns, link_id = link
            except ValueError as err:
                if (
                    len(link) == 3
                    and link[0] == "pl"
                    and link[1] in ["http", "https"]
                    and link[2].startswith("//pleiades.stoa.org/places/")
                ):
                    # handle malformed Pleiades links like
                    # ['pl', 'http', '//pleiades.stoa.org/places/700424']
                    ns = "pl"
                    link_id = [part for part in link[2].split("/") if part][-1]
                else:
                    logger.warning(
                        f"Skipping malformed WHG link for {self.uri}: {link}"
                    )
                    continue
            try:
                base_uri = self._context[ns]
            except KeyError:
                if ns == "pl":
                    base_uri = "https://pleiades.stoa.org/places/"
                elif ns == "wp":
                    base_uri = "https://en.wikipedia.org/wiki/"
                elif ns == "viaf":
                    base_uri = "https://viaf.org/viaf/"
                elif ns == "loc":
                    base_uri = "https://id.loc.gov/authorities/names/"
                elif ns == "gnd":
                    # at code time, GND URIs are returning 404s
                    logger.error(
                        f"GND URIs are currently not supported (404s): {link_id} for {self.uri}"
                    )
                elif ns == "bnf":
                    logger.error(
                        f"BNF URIs are currently not supported: {link_id} for {self.uri}"
                    )
                else:
                    raise NotImplementedError(
                        f"Unknown namespace abbreviation '{ns}' in WHG links for {link_id}"
                    )
            full_uri = f"{base_uri}{link_id}"
            netloc = urlparse(full_uri).netloc
            try:
                self.links[netloc]
            except KeyError:
                self.links[netloc] = list()
            self.links[netloc].append(("relatedMatch", full_uri))

        try:
            source_link = self._raw_data["@id"]
        except KeyError:
            pass
        else:
            parts = urlparse(source_link)
            domain = parts.netloc
            try:
                self.links[domain]
            except KeyError:
                self.links[domain] = list()
            self.links[domain].append(("relatedMatch", source_link))
