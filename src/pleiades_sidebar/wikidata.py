#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define a class for managing data from Wikidata
"""
import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.dataset import Dataset

logger = logging.getLogger("pleiades_sidebar")
wikidata_path = Path(environ["WIKIDATA_PATH"]).expanduser().resolve()
logger.debug(f"Wikidata path: {wikidata_path}")


class WikidataDataset(Dataset):
    def __init__(self):
        Dataset.__init__(self)
