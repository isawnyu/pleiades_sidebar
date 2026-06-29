#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from the CFL/AGO API
"""

import logging
from lxml.etree import Element, tostring
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm
from pprint import pformat
from urllib.parse import urlsplit
from validators import url as valid_url

DEFAULT_CFLAGOAPI_PATH = Path(environ["CFLAGOAPI_PATH"]).expanduser().resolve()


class CFLAGOAPIDataset(Dataset):
    def __init__(self, path: Path = DEFAULT_CFLAGOAPI_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "cflagoapi"
        if use_cache:
            Dataset.from_cache(self, namespace="mantoapi")
        else:
            Dataset.load(self, path, "xml_wfs")

    def parse_all(self):
        logger = logging.getLogger("CFLAGOAPIDataset.parse_all")
        for toponyme in self._raw_data:
            item = CFLAGOAPIDataItem(toponyme)
            try:
                self._data[item.uri]
            except KeyError:
                self._data[item.uri] = item
            else:
                logger.debug(f"CFL/AGO API URI collision: {item.uri}. Merging ...")
                for netloc, link_list in item.links.items():
                    existing_link_uris = {
                        link_uri
                        for link_type, link_uri in self._data[item.uri].links[netloc]
                    }
                    for link_type, link_uri in link_list:
                        if link_uri not in existing_link_uris:
                            self._data[item.uri].links[netloc].append(
                                (link_type, link_uri)
                            )



class CFLAGOAPIDataItem(DataItem):
    def __init__(self, raw: Element):
        DataItem.__init__(self, raw=raw)

    def _parse(self):
        """Parse/ingest the raw data for this item into label, uri, and summary fields
        OVERLOAD THIS METHOD for each dataset"""
        labels = list()
        for child in self._raw_data:
            tag = child.tag.split("}")[-1]
            # label
            if tag in {"name", "name_gr"}:
                if child.text:
                    raw_labels = [t.strip() for t in norm(child.text).split(",") if t.strip()]
                    if raw_labels:
                        labels.extend(raw_labels)
            # uri
            elif tag == "url":
                val = norm(child.text)
                if valid_url(val):
                    self.uri = val
                else:
                    raise ValueError(f"Invalid URL in CFL/AGO API data: {val}")
            # summary
                # N/A
            # links
            elif tag == "pleiades":
                if child.text:
                    val = norm(child.text)
                    if val:
                        val = f"https://pleiades.stoa.org/places/{val}"
                        if valid_url(val):
                            self.links = {"pleiades.stoa.org": [val]}
                        else:
                            raise ValueError(f"Invalid Pleiades URL in CFL/AGO API data: {val}")
        # post-prcess labels
        labels = list(dict.fromkeys(labels))  # remove duplicates while preserving order
        self.label = ", ".join(labels)

