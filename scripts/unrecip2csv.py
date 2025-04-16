#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2025 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Convert unreciprocated JSON into CSV
"""

from airtight.cli import configure_commandline
import csv
import json
import logging
from pathlib import Path
from slugify import slugify

logger = logging.getLogger(__name__)

DEFAULT_LOG_LEVEL = logging.WARNING
OPTIONAL_ARGUMENTS = [
    [
        "-l",
        "--loglevel",
        "NOTSET",
        "desired logging level ("
        + "case-insensitive string: DEBUG, INFO, WARNING, or ERROR",
        False,
    ],
    ["-v", "--verbose", False, "verbose output (logging level == INFO)", False],
    [
        "-w",
        "--veryverbose",
        False,
        "very verbose output (logging level == DEBUG)",
        False,
    ],
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
    ["where", str, "path to dir containing unrecip files"]
]


def main(**kwargs):
    """
    main function
    """
    # logger = logging.getLogger(sys._getframe().f_code.co_name)
    path = Path(kwargs["where"]).expanduser().resolve()
    for file in path.glob("unreciprocated_*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        del f
        rows = list()
        for item in data:
            d = dict()
            d["uri"] = item["@id"]
            d["title"] = item["properties"]["title"]
            d["summary"] = item["properties"]["summary"]
            d["pleiades_uri"] = [
                i["identifier"]
                for i in item["links"]
                if "pleiades.stoa.org" in i["identifier"]
            ][0]
            rows.append(d)
        rows = sorted(rows, key=lambda r: slugify(r["title"], separator=""))
        csv_filename = f"{file.stem}.csv"
        csv_filepath = path / csv_filename
        with open(csv_filepath, "w", newline="") as csvfile:
            fieldnames = list(rows[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        del csvfile
        logger.info(f"Wrote {csv_filepath}")


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
