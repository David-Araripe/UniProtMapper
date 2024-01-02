# -*- coding: utf-8 -*-
"""Module contains the implementation of the command-line interface"""

import argparse
import csv
import sys
from io import StringIO
from itertools import cycle
from pathlib import Path

from .api import ProtMapper

CROSSREF_PATH = Path(__file__).parent / "resources/uniprot_mapping_dbs.json"
FIELDS_CONFIG_PATH = Path(__file__).parent / "resources/cli_return_fields.txt"


def print_colored_csv(csv_io):
    """Function to make a colored output of a csv file. Source for the color codes:
    https://www.kaggle.com/discussions/general/273188"""

    # codes for red, green, yellow, blue, cyan, white
    color_codes = [31, 32, 33, 34, 36, 37]
    color_iterator = cycle(color_codes)

    csv_io.seek(0)  # Ensure you're at the start of the StringIO object
    reader = csv.reader(csv_io)
    for row in reader:
        for i, col in enumerate(row):
            color_code = next(color_iterator)
            if i < len(row) - 1:  # not the last column
                print(f"\033[1;{color_code};40m{col}\033[1;37;40m,", end="")
            else:  # last column, don't print comma after
                print(f"\033[1;{color_code};40m{col}", end=" ")
        print("\033[0m")  # reset color
        color_iterator = cycle(color_codes)  # reset colors for each row


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="UniProtMapper",
        description=(
            "Retrieve data from UniProt using UniProt's RESTful API. For a list of "
            "all available fields, see: https://www.uniprot.org/help/return_fields. "
            "Alternatively, use the --print-fields argument to print the available "
            "fields and exit the program."
        ),
    )
    parser.add_argument(
        "-i",
        "--ids",
        nargs="*",
        required=True,
        help=(
            "List of UniProt IDs to retrieve information from. "
            "Values must be separated by spaces."
        ),
    )
    parser.add_argument(
        "-r",
        "--return-fields",
        nargs="*",
        help=(
            "If not defined, will pass `None`, returning all available fields. "
            "Else, values should be fields to be returned separated by spaces. "
            "See --print-fields for available options."
        ),
    )
    parser.add_argument(
        "--default-fields",
        "-def",
        action="store_true",
        default=False,
        help=(
            "This option will override the --return-fields option. "
            f"Returns only the default fields stored in: {str(FIELDS_CONFIG_PATH)}"
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help=(
            "Path to the output file to write the returned fields. "
            "If not provided, will write to stdout. "
        ),
    )
    parser.add_argument(
        "-from",
        "--from-db",
        type=str,
        default="UniProtKB_AC-ID",
        help=(
            "The database from which the IDs are. For the available cross references, "
            f"see: {CROSSREF_PATH}"
        ),
    )
    parser.add_argument(
        "-to",
        "--to-db",
        type=str,
        default="UniProtKB-Swiss-Prot",
        help=(
            "The database to which the IDs will be mapped. For the available cross references, "
            f"see: {CROSSREF_PATH}"
        ),
    )
    parser.add_argument(
        "-over",
        "--overwrite",
        action="store_true",
        help="If desired to overwrite an existing file when using -o/--output",
    )
    parser.add_argument(
        "-pf",
        "--print-fields",
        action="store_true",
        help="Prints the available return fields and exits the program.",
    )

    if any(["--print-fields" in sys.argv, "-pf" in sys.argv]):
        print("Available return fields:")
        result = ProtMapper().fields_table
        csv_io = StringIO(result.to_csv(index=False))
        print_colored_csv(csv_io)
        sys.exit()

    return parser.parse_args()


def main():
    with FIELDS_CONFIG_PATH.open("r") as f:
        DEFAULT_FIELDS = f.read().splitlines()

    args = parse_arguments()

    field_retriever = ProtMapper(
        pooling_interval=5, total_retries=5, backoff_factor=0.5
    )
    if args.default_fields:
        args.return_fields = DEFAULT_FIELDS
    result, failed = field_retriever.get(
        args.ids, fields=args.return_fields, from_db=args.from_db, to_db=args.to_db
    )
    field_retriever.session.close()
    if failed:
        print(f"Failed to retrieve {len(failed)} IDs:\n {failed}")

    if args.output is not None:
        output_path = Path(args.output)
        if output_path.exists():
            if not args.overwrite:
                raise FileExistsError(
                    f"Input file {output_path} already exists. "
                    "Use parameter --overwrite to overwrite it."
                )
        result.to_csv(args.output, index=False)
    else:
        csv_io = StringIO(result.to_csv(index=False))
        print_colored_csv(csv_io)
