#
# This file is part of pleiades_sidebar
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2024 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Python 3 script template (changeme)
"""

from airtight.cli import configure_commandline
import json
import logging
from os import environ
from pathlib import Path
from pleiades_sidebar.generator import Generator
from pprint import pprint, pformat
from slugify import slugify

logger = logging.getLogger(__name__)

DEFAULT_NAMESPACES = environ.get("SIDEBAR_NAMESPACES")
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
    ["-c", "--usecache", False, "use cached data", False],
    [
        "-n",
        "--namespaces",
        DEFAULT_NAMESPACES,
        "comma-separated list of namespaces to load",
        False,
    ],
    [
        "-o",
        "--output",
        "",
        "path to directory into which to write output JSON files",
        False,
    ],
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
]


def main(**kwargs):
    """
    main function
    """
    namespaces = [ns.strip() for ns in kwargs["namespaces"].split(",")]
    g = Generator(namespaces)
    p, unrecip = g.generate()
    outpath = kwargs["output"].strip()
    if outpath:
        outpath = Path(outpath).expanduser().resolve()
        if not outpath.exists():
            outpath.mkdir()
        if outpath.is_dir():
            for puri, data in p.items():
                pid = puri.split("/")[-1]
                try:
                    dirpath = outpath / pid[0] / pid[1] / pid[2]
                except IndexError as err:
                    err.add_note(f"Failed creation of output path from puri: '{puri}'")
                    raise err
                dirpath.mkdir(parents=True, exist_ok=True)
                filepath = dirpath / f"{pid}.json"
                if not filepath.is_file():
                    # don't write a file at all if we don't have content, unless we are
                    # overwriting a file that's already there
                    if len(data) == 0:
                        logger.warning(
                            f"Skipped writing {filepath} because there is no data content and the file did not already exist."
                        )
                        continue
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                del f
            logger.info(f"Wrote sidebar JSON to {str(outpath)}")
            for ns, data in unrecip.items():
                pathsafe_ns = slugify(ns, separator="_")
                filepath = outpath / f"unreciprocated_{pathsafe_ns}.json"
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                del f
        else:
            logger.error(
                f"Could not write JSON because outpath is not a directory: {outpath}"
            )
    else:
        s = json.dumps(p, ensure_ascii=False, indent=4)
        print(s)


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
