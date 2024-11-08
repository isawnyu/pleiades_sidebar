#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from Itiner-e
"""
import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset, DataItem
from pleiades_sidebar.norm import norm
from pprint import pformat
from urllib.parse import urlparse
from validators import url as valid_url

DEFAULT_NOMISMA_PATH = Path(environ["NOMISMA_PATH"]).expanduser().resolve()


class NomismaDataset(Dataset):
    def __init__(self, path: Path = DEFAULT_NOMISMA_PATH, use_cache=False):
        Dataset.__init__(self)
        self.namespace = "nomisma"
        if use_cache:
            Dataset.from_cache(self, namespace=self.namespace)
        else:
            Dataset.load(self, path, "jsonld")

    def parse_all(self):
        logger = logging.getLogger("NomismaDataset.parse_all")
        for raw_item in self._raw_data:
            try:
                raw_item["@type"]
            except KeyError:
                logger.error(f"No @type in {pformat(raw_item, indent=4)}")
                continue

            if "nmo:Mint" not in raw_item["@type"]:
                continue
            item = NomismaDataItem(raw_item)
            try:
                self._data[item.uri]
            except KeyError:
                self._data[item.uri] = item
            else:
                logger.debug(f"Nomisma URI collision: {item.uri}. Merging ...")
                self._data[item.uri].links["pleiades.stoa.org"].extend(
                    item.links["pleiades.stoa.org"]
                )


class NomismaDataItem(DataItem):
    def __init__(self, raw: dict):
        DataItem.__init__(self, raw=raw)
        self._raw_data = raw

    def _parse(self):
        """Parse the Nomisma ndjson export format"""

        logger = logging.getLogger("NomismaDataItem._parse")

        # label
        if isinstance(self._raw_data["skos:prefLabel"], dict):
            self.label = norm(self._raw_data["skos:prefLabel"]["@value"])
        elif isinstance(self._raw_data["skos:prefLabel"], list):
            self.label = norm(
                [
                    label["@value"]
                    for label in self._raw_data["skos:prefLabel"]
                    if label["@language"] == "en"
                ][0]
            )
        else:
            raise TypeError(
                f"skos:prefLabel type='{type(self._raw_data['skos:prefLabel'])}"
            )

        # uri
        self.uri = (
            self._get_base_uri("nomisma") + self._raw_data["@id"].split(":")[1].strip()
        )

        # summary
        # self.summary = norm(self._raw_data["skos:definition"]["@value"])
        try:
            self._raw_data["skos:definition"]
        except KeyError:
            logger.warning(
                f"No skos:definition for {pformat(self._raw_data, indent=4)}"
            )
        else:
            if isinstance(self._raw_data["skos:definition"], dict):
                self.summary = norm(self._raw_data["skos:definition"]["@value"])
            elif isinstance(self._raw_data["skos:definition"], list):
                self.summary = norm(
                    [
                        summary["@value"]
                        for summary in self._raw_data["skos:definition"]
                        if summary["@language"] == "en"
                    ][0]
                )
            else:
                raise TypeError(
                    f"skos:definition type='{type(self._raw_data['skos:definition'])}"
                )

        # links
        # close_match = self._raw_data["skos:closeMatch"]["@id"]
        # if "pleiades.stoa.org" in close_match:
        #    self.links = {"pleiades.stoa.org": []}
        try:
            self._raw_data["skos:closeMatch"]
        except KeyError:
            try:
                self._raw_data["skos:definition"]
            except KeyError:
                logger.error(
                    f"No skos:closeMatch and no skos:definition for {pformat(self._raw_data, indent=4)}"
                )
                return
            else:
                logger.error(
                    f"No skos:closeMatch for @id={self._raw_data['@id']}: {pformat(self._raw_data['skos:definition'], indent=4)}"
                )
            return

        if isinstance(self._raw_data["skos:closeMatch"], dict):
            close_matches = [norm(self._raw_data["skos:closeMatch"]["@id"])]
        elif isinstance(self._raw_data["skos:closeMatch"], list):
            close_matches = [
                norm(cm["@id"]) for cm in self._raw_data["skos:closeMatch"]
            ]
        else:
            raise TypeError(
                f"skos:closeMatch type='{type(self._raw_data['skos:closeMatch'])}"
            )
        close_matches = [cm for cm in close_matches if valid_url(cm)]
        for cm in close_matches:
            parts = urlparse(cm)
            try:
                self.links[parts.netloc]
            except KeyError:
                self.links[parts.netloc] = list()
            if cm not in self.links[parts.netloc]:
                self.links[parts.netloc].append(cm)
