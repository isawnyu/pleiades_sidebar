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
from pleiades_sidebar.itinere import ItinerEDataset
from pleiades_sidebar.pleiades import PleiadesDataset
from pleiades_sidebar.wikidata import WikidataDataset

CLASSES_BY_NAMESPACE = {"wikidata": WikidataDataset, "itinere": ItinerEDataset}


class Generator:
    def __init__(self, namespaces: list, paths: dict = {}, use_cached: bool = False):
        self.datasets = {}
        try:
            self._pleiades_path = paths["pleiades"]
        except KeyError:
            self._pleiades_path = None
        for ns in namespaces:
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

        sidebar = dict()
        for ns, dataset in self.datasets.items():
            matches = dataset.get_pleiades_matches()
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
                for ditem in data_items:
                    ditem_lpf = ditem.to_lpf_dict()
                    if ditem.uri in these_pleiades_links:
                        ditem_lpf["properties"]["reciprocal"] = True
                    else:
                        ditem_lpf["properties"]["reciprocal"] = False
                    sidebar[puri].append(ditem_lpf)
        return sidebar
