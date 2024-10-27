#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the Generator module 
"""

from pathlib import Path
from pleiades_sidebar.generator import Generator
import pytest

TEST_DATA_DIR = Path("tests/data/")


class TestGenerator:

    @classmethod
    def setup_class(cls):
        # Create an instance of Generator
        cls.generator = Generator(
            namespaces=[],
        )

    def test_generator_initialization(self):

        # Check if the instance is created successfully
        assert isinstance(self.generator, Generator)

    def test_generator_from_cache(self):
        g = Generator(namespaces=["wikidata"], use_cached=True)
