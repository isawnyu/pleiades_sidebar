#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a base class for a dataset manager
"""
from copy import deepcopy
from encoded_csv import get_csv
import jsonlines
import logging
from pathlib import Path
from platformdirs import user_cache_dir
from pprint import pformat
from pickle import Pickler, Unpickler

RESOURCE_URIS = {
    "cfl/ado": "",
    "dare": "",
    "geonames": "",
    "gettytgn": "",
    "itinere": "https://itiner-e.org/route-segment/",
    "idaigaz": "",
    "loc": "",
    "manto": "",
    "nomisma": "",
    "pleiades": "https://pleiades.stoa.org/places/",
    "topostext": "",
    "trismegistos": "",
    "viaf": "",
    "vici": "",
    "wikidata": "https://wikidata.org/entities/",
}

LPF_FEATURE_COLLECTION_TEMPLATE = {
    "type": "FeatureCollection",
    "@context": "https://raw.githubusercontent.com/LinkedPasts/linked-places/master/linkedplaces-context-v1.1.jsonld",
    "features": [],
}

LPF_FEATURE_TEMPLATE = {
    "@id": None,
    "type": "Feature",
    "properties": {"title": "", "summary": ""},
    "links": [],
}


class DataItem:
    """An individual data item in a dataset"""

    def __init__(self, raw: dict):
        self.label = None
        self.uri = None
        self.summary = None
        self.links = dict()
        self._raw_data = raw
        # TBD: make spatial?
        self._parse()

    @property
    def pleiades_uris(self) -> str:
        clean_links = set()
        for link in self.links["pleiades.stoa.org"]:
            if isinstance(link, str):
                clean_links.add(link)
            elif isinstance(link, tuple):
                clean_links.add(link[1])
        return list(clean_links)

    def to_lpf_dict(self):
        """Get LPF formatted dictionary, suitable to save as JSON"""
        d = deepcopy(LPF_FEATURE_TEMPLATE)
        d["@id"] = self.uri
        d["properties"]["title"] = self.label
        d["properties"]["summary"] = self.summary
        link_uris = set()
        for domain_links in self.links.values():
            for link in domain_links:
                if isinstance(link, str):
                    if link not in link_uris:
                        link_uris.add(link)
                        dl = {"type": "closeMatch", "identifier": link}
                    else:
                        continue
                elif isinstance(link, tuple) and len(link) == 2:
                    if link[1] not in link_uris:
                        link_uris.add(link[1])
                        dl = {"type": link[0], "identifier": link[1]}
                    else:
                        continue
                else:
                    raise ValueError(type(link))
                d["links"].append(dl)
        return d

    def __repr__(self) -> str:
        d = {
            "label": self.label,
            "uri": self.uri,
            "summary": self.summary,
            "links": self.links,
        }
        return pformat(d, indent=4)

    def _get_base_uri(self, resource_shortname: str) -> str:
        """Get base URI for a given resource shortname"""
        try:
            return RESOURCE_URIS[resource_shortname]
        except KeyError:
            logger = logging.getLogger("_get_base_uri")
            logger.error(
                f"No base URI available for resource shortname '{resource_shortname}'"
            )
            raise NotImplementedError()

    def _parse(self):
        """Parse/ingest the raw data for this item into label, uri, and summary fields
        OVERLOAD THIS METHOD for each dataset"""
        # make sure you populate
        # label
        # uri
        # summary
        # links
        pass


class Dataset:
    """Base class for a dataset manager"""

    def __init__(self):
        self.namespace = None
        # Parsed DataItems keyed by URI
        self._data = dict()
        # Dictionary of lists of DataItem IDs keyed by Pleiades URIs
        self._pleiades_index = dict()

    def from_cache(self, namespace: str):
        path = Path(user_cache_dir("pleiades_sidebar", ensure_exists=True))
        with open(path / f"{self.namespace}.pickle", "rb") as f:
            unpickler = Unpickler(f)
            self._data = unpickler.load()
        del f
        self._pindex()

    def get(self, item_uri: str) -> DataItem:
        """Get a parsed dataitem by its URI"""
        try:
            return self._data[item_uri]
        except KeyError:
            return None

    def get_pleiades(self, pleiades_uri: str) -> list:
        """Return a list of IDs for all items in this dataset that correspond to a Pleiades URI"""
        try:
            return self._pleiades_index[pleiades_uri]
        except KeyError:
            return list()

    def get_pleiades_matches(self, omit_multiples=False) -> dict:
        """Return a dictionary with keys == pleiades_uris and values the matching database items"""
        result = dict()
        for puri, uris in self._pleiades_index.items():
            if omit_multiples and len(uris) > 1:
                pass
            else:
                result[puri] = [self._data[uri] for uri in uris]
        return result

    def load(self, datafile_path: Path, load_method: str):
        """Load the target dataset"""
        cmd = f"_load_{load_method}"
        getattr(self, cmd)(datafile_path)
        self.parse_all()
        self.to_cache()
        self._pindex()

    def parse_all(self):
        """Parse the already-loaded dataset"""
        # OVERRIDE THIS METHOD FOR EACH DATASET
        pass

    def _pindex(self):
        logger = logging.getLogger("Dataset._pindex")
        for ditem in self._data.values():
            for puri in ditem.pleiades_uris:
                try:
                    self._pleiades_index[puri]
                except KeyError:
                    self._pleiades_index[puri] = set()
                else:
                    logger.debug(
                        f"Pleiades URI collision: {puri} in {ditem.uri} and {self._pleiades_index[puri]}"
                    )
                self._pleiades_index[puri].add(ditem.uri)

    def to_cache(self):
        path = Path(user_cache_dir("pleiades_sidebar", ensure_exists=True))
        with open(path / f"{self.namespace}.pickle", "wb") as f:
            pickler = Pickler(f)
            pickler.dump(self._data)
        del f

    def to_lpf_dict(self):
        d = deepcopy(LPF_FEATURE_COLLECTION_TEMPLATE)
        d["features"] = [item.to_lpf_dict() for item in self._data.values()]
        return d

    def _load_csv(self, datafile_path: Path):
        data = get_csv(str(datafile_path), sample_lines=1000)
        logger = logging.getLogger("_load_csv")
        logger.debug(
            f"Loaded {len(data['content'])} rows of data with fieldnames: {pformat(data['fieldnames'], indent=4)}"
        )
        self._raw_data = data["content"]

    def _load_ndjson(self, datafile_path: Path):
        with jsonlines.open(str(datafile_path)) as reader:
            self._raw_data = [obj for obj in reader]
        del reader

    def _load_tsv(self, datafile_path: Path):
        data = get_csv(str(datafile_path), dialect="excel-tab", sample_lines=1000)
        logger = logging.getLogger("_load_tsv")
        logger.debug(
            f"Loaded {len(data['content'])} rows of data with fieldnames: {pformat(data['fieldnames'], indent=4)}"
        )
        self._raw_data = data["content"]

    def __len__(self):
        return len(self._data)
