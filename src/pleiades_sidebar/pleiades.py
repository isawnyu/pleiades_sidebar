#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
On-demand Pleiades dataset
"""
import json
from logging import getLogger
from os import environ
from os.path import join as pathjoin
from pathlib import Path

DEFAULT_PLEIADES_PATH = Path(environ["PLEIADES_PATH"]).expanduser().resolve()


class PleiadesDataset:
    def __init__(self, path: Path = DEFAULT_PLEIADES_PATH):
        self._path = path
        self._places = dict()

    @property
    def path(self):
        return self._path

    def get(self, puri: str) -> dict:
        logger = getLogger("PleiadesDataset.get")
        try:
            return self._places[puri]
        except KeyError:
            pid = [s for s in puri.split("/") if s.strip()][-1]
            parts = list(pid)
            parts = parts[0 : len(parts) - 2]
            parts.append(pid)
            ppath = self._path / "{}.json".format(pathjoin(*parts))
            logger.debug(f"ppath='{ppath}'")
            # paths = list(self._path.glob(f"**/{pid}.json"))
            # if len(paths) != 1:
            #    raise RuntimeError(f"puri='{puri}', pid='{pid}', paths={paths}")
            with open(ppath, "r", encoding="utf-8") as f:
                self._places[puri] = json.load(f)
            del f
            return self._places[puri]
