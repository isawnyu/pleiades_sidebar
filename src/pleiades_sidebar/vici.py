#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from vici.org
"""

import logging
from os import environ
from pathlib import Path
from venv import logger
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm
from pprint import pformat
from urllib.parse import urlsplit
from validators import url as validate_url

DEFAULT_VICI_PATH = Path(environ["VICI_PATH"]).expanduser().resolve()


class VICIDataset(Dataset):
    def __init__(self, path: Path = DEFAULT_VICI_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "vici"
        if use_cache:
            Dataset.from_cache(self, namespace="vici")
        else:
            Dataset.load(self, path, "json")

    def parse_all(self):
        logger = logging.getLogger("VICIDataset.parse_all")
        for raw_item in self._raw_data["results"]["bindings"]:  # type: ignore
            try:
                this_item = VICIDataItem(raw_item)
            except ValueError as e:
                logger.error(f"Error parsing raw item: {e}\n{pformat(raw_item)}")
                continue
            try:
                self._data[this_item.uri]
            except KeyError:
                self._data[this_item.uri] = this_item
            else:
                self._data[this_item.uri].merge(this_item)


class VICIDataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def merge(self, other):
        """Merge another VICIDataItem into this one"""
        logger = logging.getLogger("VICIDataItem.merge")
        logger.debug(f"Merging VICIDataItem:\n{pformat(other)}\ninto\n{pformat(self)}")
        # uri
        if self.uri != other.uri:
            raise ValueError(
                f"Cannot merge items with different URIs: {self.uri} vs {other.uri}"
            )
        else:
            # already the same, so no action needed
            pass

        # labels
        for language, label in other.labels_by_language.items():
            if language not in self.labels_by_language:
                self.labels_by_language[language] = label
            elif self.labels_by_language[language] != label:
                raise ValueError(
                    f"Label conflict for {self.uri} in language '{language}' during merge: '{self.labels_by_language[language]}' vs '{label}'. Keeping existing."
                )
        for lang in ["und", "en", "de", "fr", "es", "it", "nl"]:
            try:
                self.label = self.labels_by_language[lang]
            except KeyError:
                continue
            else:
                break

        for other_netloc, other_links in other.links.items():
            union_links = set(self.links.get(other_netloc, []))
            union_links.update([link for link in other_links if validate_url(link)])
            if union_links:
                self.links[other_netloc] = sorted(union_links)

        logger.debug(f"Merge complete. Resulting item:\n{pformat(self)}")

    def _parse(self):
        """Parse vici.org CSV data
        self.uri = None
        self.label = None (replace with property?)
        self.labels_by_language = dict()
        self.summary = None
        self.links = dict() - by domain
        """

        # uri
        vici_uri = norm(self._raw_data["viciURI"]["value"])
        if not validate_url(vici_uri):
            raise ValueError(f"Invalid vici.org URI: {vici_uri}")
        parts = urlsplit(vici_uri)
        if parts.scheme == "http":
            vici_uri = vici_uri.replace("http://", "https://")
        self.uri = vici_uri

        # labels
        raw_label = norm(self._raw_data["label"]["value"])
        try:
            language = self._raw_data["label"]["xml:lang"]
        except KeyError:
            language = "und"  # undetermined
        self.labels_by_language[language] = raw_label
        self.label = raw_label  # default label (merge may change this)

        # summary
        # TBD, not currently grabbing this in the SPARQL query, but may want to in the future

        # links
        raw_link = norm(self._raw_data["linkURI"]["value"])
        if validate_url(raw_link):
            parts = urlsplit(raw_link)
            if parts.netloc == "pleiades.stoa.org" and parts.scheme == "http":
                raw_link = raw_link.replace("http://", "https://")
            self.links[parts.netloc] = [
                raw_link,
            ]
        else:
            raise ValueError(f"Invalid link URL: {raw_link}")
        logger = logging.getLogger("VICIDataItem._parse")
        logger.debug(
            f"Parsed VICIDataItem: uri='{self.uri}', label='{self.label}', links={self.links}"
        )
