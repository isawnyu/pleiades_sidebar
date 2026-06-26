#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from the MANTO API
"""

import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm
from pprint import pformat
from urllib.parse import urlsplit

DEFAULT_MANTOAPI_PATH = Path(environ["MANTOAPI_PATH"]).expanduser().resolve()


class MANTOAPIDataset(Dataset):
    def __init__(self, path: Path = DEFAULT_MANTOAPI_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "mantoapi"
        if use_cache:
            Dataset.from_cache(self, namespace="mantoapi")
        else:
            Dataset.load(self, path, "json")

    def parse_all(self):
        logger = logging.getLogger("MANTOAPIDataset.parse_all")
        for raw_item_id, raw_item in self._raw_data["data"]["objects"].items():  # type: ignore
            if not raw_item:
                logger.warning(f"Skipping empty raw item: {raw_item_id}")
                continue
            if (
                raw_item["object_definitions"]["18819"]["object_definition_value"]
                != "Place"
            ):
                logger.info(f"Skipping non-Place object: {raw_item_id}")
                continue
            try:
                this_item = MANTOAPIDataItem(raw_item)
            except ValueError as e:
                logger.error(f"Error parsing raw item: {e}\n{pformat(raw_item)}")
                continue
            manto_uri = f"https://resource.manto.unh.edu/{raw_item_id}"
            try:
                self._data[manto_uri]
            except KeyError:
                self._data[manto_uri] = this_item
            else:
                raise ValueError(f"Duplicate MANTO API URI found: {manto_uri}")
            print(self._data[manto_uri].label)


class MANTOAPIDataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse/ingest the raw data for this item into label, uri, and summary fields
        OVERLOAD THIS METHOD for each dataset"""

        od = self._raw_data["object_definitions"]
        # make sure you populate
        # label
        raw_label = []
        for key in ["17800", "29347"]:
            this_od = od.get(key)
            if this_od:
                val = this_od.get("object_definition_value", "")
                if val:
                    val = norm(val)
                    if val:
                        raw_label.append(val)
        raw_label = " ".join(raw_label)
        if raw_label in self._raw_data["object"]["object_name"]:
            self.label = raw_label
        else:
            raise ValueError(
                f"Raw label '{raw_label}' not found in object name '{self._raw_data['object_name']}'"
            )

        # uri
        raw_uri = "https://resource.manto.unh.edu/" + norm(
            str(self._raw_data["object"]["object_id"])
        )
        self.uri = raw_uri

        # summary
        val = od.get("18818", {})
        if val:
            val = val.get("object_definition_value", "")
            if val:
                val = norm(val)
                if val:
                    self.summary = val

        # links
        for key, base_uri in {
            "18823": "https://pleiades.stoa.org/places/",
            "32773": "https://wikidata.org/wiki/",
            "32765": "https://palp.art/browse/",
            "32837": "https://www.trismegistos.org/place/",
            "33944": "",  # sic: for topostext, MANTO encodes full URIs
        }.items():
            this_od = od.get(key)
            if this_od:
                val = this_od.get("object_definition_value", "")
                if val:
                    if isinstance(val, list):
                        for v in val:
                            v = norm(v)
                            if v:
                                link = base_uri + v
                                parts = urlsplit(link)
                                try:
                                    self.links[parts.netloc]
                                except KeyError:
                                    self.links[parts.netloc] = set()
                                self.links[parts.netloc].add(link)
                    elif isinstance(val, str):
                        val = norm(val)
                        if val:
                            link = base_uri + val
                            parts = urlsplit(link)
                            try:
                                self.links[parts.netloc]
                            except KeyError:
                                self.links[parts.netloc] = set()
                            self.links[parts.netloc].add(link)
                    else:
                        raise TypeError(
                            f"Expected list value for link with key {key}, got {type(val)}:\n{pformat(this_od)}"
                        )
        for netloc, links in self.links.items():
            self.links[netloc] = sorted(links)
