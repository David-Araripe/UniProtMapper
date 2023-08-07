# -*- coding: utf-8 -*-
"""Module contains the implementation of the command-line interface"""

import argparse
import csv
from io import StringIO
from itertools import cycle
from pathlib import Path

from UniProtMapper import UniProtRetriever


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


def main():
    config_path = Path(__file__).parent / "resources/cli_return_fields.txt"
    with config_path.open("r") as f:
        DEFAULT_FIELDS = f.read().splitlines()

    parser = argparse.ArgumentParser(
        prog="UniProtMapper",
        description=(
            "Retrieve data from UniProt using the UniProt RESTful API. \nFor a list of "
            "all available fields, see: https://www.uniprot.org/help/return_fields"
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
            "List of values to be returned. Values must be separated by spaces. "
            f"If not provided, will use values from config file at {str(config_path)}"
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
        "--overwrite",
        action="store_true",
        help="If desired to overwrite an existing file.",
    )
    args = parser.parse_args()

    field_retriever = UniProtRetriever(
        pooling_interval=5, total_retries=5, backoff_factor=0.5
    )
    if not args.return_fields:
        args.return_fields = DEFAULT_FIELDS

    result, failed = field_retriever.retrieveFields(args.ids, fields=args.return_fields)
    field_retriever.session.close()
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
