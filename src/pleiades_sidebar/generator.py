#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for generating sidebar data from multiple sources
"""

from os import environ
from pleiades_sidebar.itinere import ItinerEDataset
from pleiades_sidebar.wikidata import WikidataDataset

CLASSES_BY_NAMESPACE = {"wikidata": WikidataDataset, "itinere": ItinerEDataset}


class Generator:
    def __init__(self, namespaces: list, paths: dict = {}, use_cached: bool = False):
        self.datasets = {}
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
        pleiades = dict()
        for ns, dataset in self.datasets.items():
            matches = dataset.get_pleiades_matches()
            for puri, data_items in matches.items():
                try:
                    pleiades[puri]
                except KeyError:
                    pleiades[puri] = list()
                pleiades[puri].extend([ditem.to_lpf_dict() for ditem in data_items])
        return pleiades
