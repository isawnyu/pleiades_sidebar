#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024-2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from Paths Atlas
"""
import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm
from pprint import pformat
import re
from urllib.parse import urlparse
from validators import url as valid_url

DEFAULT_PATHS_ATLAS_PATH = Path(environ["PATHS_ATLAS_PATH"]).expanduser().resolve()
RX_PLEIADES_NAME_URI = re.compile(
    r"^(?P<puri>https://pleiades.stoa.org/places/\d+)/[a-z]+/?$"
)


class PathsAtlasDataset(Dataset):
    def __init__(self, path: Path = DEFAULT_PATHS_ATLAS_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "paths_atlas"
        if use_cache:
            Dataset.from_cache(self, namespace=self.namespace)
        else:
            Dataset.load(self, path, "json")

    def parse_all(self):
        logger = logging.getLogger("PathsAtlasDataset.parse_all")

        print

        paths_places = {
            uri: vals
            for uri, vals in self._raw_data.items()
            if uri.startswith("http://paths.uniroma1.it/atlas/places/")
            or uri.startswith("https://atlas.paths-erc.eu/places/")
        }
        for uri, raw_item in paths_places.items():
            item = PathsAtlasDataItem(raw_item)
            parts = urlparse(uri)
            if parts.hostname == "paths.uniroma1.it":
                item.uri = uri.replace(
                    "http://paths.uniroma1.it", "https://atlas.paths-erc.eu"
                )
            else:
                item.uri = uri
            try:
                self._data[item.uri]
            except KeyError:
                self._data[item.uri] = item
            else:
                logger.debug(f"Paths Atlas URI collision: {item.uri}. Merging ...")
                self._data[item.uri].links["pleiades.stoa.org"].extend(
                    item.links["pleiades.stoa.org"]
                )


class PathsAtlasDataItem(DataItem):
    def __init__(self, raw: dict):
        if not isinstance(raw, dict):
            raise TypeError(type(raw))
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse the Paths Atlas json export format"""

        logger = logging.getLogger("PathsAtlasDataItem._parse")

        # label
        self.label = norm(
            [
                label["value"]
                for label in self._raw_data[
                    "http://www.w3.org/2000/01/rdf-schema#label"
                ]
                if label["lang"] == "en"
            ][0]
        )

        # uri
        # only available in key associated with this dictionary, so not at this level

        # summary
        # Paths doesn't provide

        # links
        try:
            matches = [
                m["value"]
                for m in self._raw_data[
                    "http://www.w3.org/2004/02/skos/core#exactMatch"
                ]
            ]
        except KeyError:
            matches = list()
        for cm in matches:
            parts = urlparse(cm)
            try:
                self.links[parts.netloc]
            except KeyError:
                self.links[parts.netloc] = list()
            if cm not in self.links[parts.netloc]:
                m = RX_PLEIADES_NAME_URI.match(cm)
                if m is not None:
                    self.links[parts.netloc].append(m.group("puri"))
                elif cm[-1] == "/":
                    self.links[parts.netloc].append(cm[:-1])
                else:
                    self.links[parts.netloc].append(cm)
