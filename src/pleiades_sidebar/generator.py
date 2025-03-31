#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for generating sidebar data from multiple sources
"""
import logging
from os import environ
from pleiades_sidebar.cfl_ago import CFLAGODataset
from pleiades_sidebar.edh_geo import EDHGEODataset
from pleiades_sidebar.itinere import ItinerEDataset
from pleiades_sidebar.manto import MANTODataset
from pleiades_sidebar.nomisma import NomismaDataset
from pleiades_sidebar.pleiades import PleiadesDataset
from pleiades_sidebar.temples_classical_world import ClassicalTemplesDataset
from pleiades_sidebar.wikidata import WikidataDataset
from urllib.parse import urlparse, parse_qs
from validators import url as valid_uri

CLASSES_BY_NAMESPACE = {
    "cflago": CFLAGODataset,
    "edhgeo": EDHGEODataset,
    "itinere": ItinerEDataset,
    "manto": MANTODataset,
    "nomisma": NomismaDataset,
    "classical_temples": ClassicalTemplesDataset,
    "wikidata": WikidataDataset,
}


class Generator:
    def __init__(self, namespaces: list, paths: dict = {}, use_cached: bool = False):
        logger = logging.getLogger("Generator.__init__")
        self.datasets = {}
        try:
            self._pleiades_path = paths["pleiades"]
        except KeyError:
            self._pleiades_path = None
        for ns in namespaces:
            logger.info(f"Loading data from namespace {ns}")
            try:
                path = paths[ns]
            except KeyError:
                self.datasets[ns] = CLASSES_BY_NAMESPACE[ns](use_cache=use_cached)
            else:
                self.datasets[ns] = CLASSES_BY_NAMESPACE[ns](
                    path=path, use_cache=use_cached
                )

    def generate(self):
        logger = logging.getLogger("Generator.generate")
        if self._pleiades_path is not None:
            pleiades = PleiadesDataset(self._pleiades_path)
        else:
            pleiades = PleiadesDataset()
        pleiades_links = dict()

        # sidebar:
        # data for consumption by sidebar widget on Pleiades website
        # keys are pleiades uris
        # values are lists of third-party matches, each represented by a dictionary
        # using abbreviated Linked Places Format
        sidebar = dict()

        # unreciprocated:
        # data to use to guide supervised work adding unreciprocated outside links
        # keys are external namespaces
        # values are lists of third-party matches in that namespace which are unreciprocated
        # by Pleiades, each represented by a dictionary using abbreviated Linked Places Format
        unreciprocated = dict()

        all_match_count = 0  # total number of matches
        all_reciprocal_count = 0  # total number of reciprocated matches

        for ns, dataset in self.datasets.items():
            unreciprocated[ns] = list()
            matches = dataset.get_pleiades_matches()
            all_match_count += len(matches)

            logger.info(
                f"Checking for Pleiades reciprocity in {len(matches)} links from the {ns} dataset."
            )
            for puri, data_items in matches.items():
                try:
                    sidebar[puri]
                except KeyError:
                    sidebar[puri] = list()
                try:
                    these_pleiades_links = pleiades_links[puri]
                except KeyError:
                    pleiades_links[puri] = set()
                    try:
                        pleiades_place = pleiades.get(puri)
                    except FileNotFoundError:
                        logger.error(
                            f"Non-existent Pleiades place {puri} referenced in {ns}. Ignored."
                        )
                        continue
                    for r in pleiades_place["references"]:
                        if r["accessURI"]:
                            pleiades_links[puri].add(r["accessURI"])
                    these_pleiades_links = pleiades_links[puri]
                normalized_pleiades_links = set()
                for this_pleiades_link in these_pleiades_links:
                    if valid_uri(this_pleiades_link):
                        parts = urlparse(this_pleiades_link)
                    else:
                        continue
                    domain = parts.netloc
                    if domain.startswith("www."):
                        domain = domain[4:]
                    query = parse_qs(parts.query)
                    try:
                        id_list = query["id"]
                    except KeyError:
                        id_list = list()
                    else:
                        if len(id_list) == 1:
                            probable_id = id_list[0].strip()
                        else:
                            id_list = list()
                    if not id_list:
                        path = [p.strip() for p in parts.path.split("/") if p.strip()]
                        try:
                            probable_id = path[-1]
                        except IndexError:
                            continue
                    normalized_pleiades_links.add(f"{domain}:{probable_id}")
                for ditem in data_items:
                    parts = urlparse(ditem.uri)
                    domain = parts.netloc
                    if domain.startswith("www."):
                        domain = domain[4:]
                    query = parse_qs(parts.query)
                    try:
                        id_list = query["id"]
                    except KeyError:
                        id_list = list()
                    else:
                        if len(id_list) == 1:
                            probable_id = id_list[0].strip()
                        else:
                            id_list = list()
                    if not id_list:
                        path = [p.strip() for p in parts.path.split("/") if p.strip()]
                        try:
                            probable_id = path[-1]
                        except IndexError as err:
                            err.add_note(ditem.uri)
                            raise err

                    normalized_item_uri = f"{domain}:{probable_id}"
                    ditem_lpf = ditem.to_lpf_dict()
                    if normalized_item_uri in normalized_pleiades_links:
                        ditem_lpf["properties"]["reciprocal"] = True
                        all_reciprocal_count += 1
                    else:
                        ditem_lpf["properties"]["reciprocal"] = False
                        unreciprocated[ns].append(ditem_lpf)
                    sidebar[puri].append(ditem_lpf)

        # sort data to facilitate run-to-run diff
        for puri in sidebar.keys():
            raw_ditems = sidebar[puri]
            cooked_ditems = list()
            for raw_ditem in raw_ditems:
                cooked_ditem = raw_ditem
                cooked_links = sorted(
                    raw_ditem["links"], key=lambda link: link["identifier"]
                )
                cooked_ditem["links"] = cooked_links
                cooked_ditems.append(cooked_ditem)
            sidebar[puri] = sorted(cooked_ditems, key=lambda d: d["@id"])
        for ns in unreciprocated.keys():
            raw_ditems = unreciprocated[ns]
            cooked_ditems = list()
            for raw_ditem in raw_ditems:
                cooked_ditem = raw_ditem
                cooked_links = sorted(
                    raw_ditem["links"], key=lambda link: link["identifier"]
                )
                cooked_ditem["links"] = cooked_links
                cooked_ditems.append(cooked_ditem)
            unreciprocated[ns] = sorted(cooked_ditems, key=lambda d: d["@id"])

        logger.info(
            f"There are {all_match_count:,} Pleiades matches across all {len(self.datasets):,} datasets "
            f"({", ".join(sorted(self.datasets.keys()))}). "
            f"{all_reciprocal_count:,} of these are reciprocated by Pleiades. "
            f"{len(sidebar):,} unique Pleiades places are referenced. "
        )
        return (sidebar, unreciprocated)
