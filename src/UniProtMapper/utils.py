# -*- coding: utf-8 -*-
"""Module with utility functions for UniProtMapper and SwissProtParser."""
import json
import re
import zlib

import pandas as pd
import pkg_resources


def read_fields_table():
    """Reads the fields table from the resources folder."""
    csv_path = pkg_resources.resource_filename(
        "UniProtMapper", "resources/uniprot_return_fields.csv"
    )
    return pd.read_csv(csv_path)


def supported_mapping_dbs():
    """Return a list of the supported datasets as UniProt cross references. This list
    is used to validate the arguments `to_db` and `from_db` in the `FieldRetriever.get()` method.
    """
    _mapping_dbs_path = pkg_resources.resource_filename(
        "UniProtMapper", "resources/uniprot_mapping_dbs.json"
    )
    with open(_mapping_dbs_path, "r") as f:
        dbs_dict = json.load(f)
    return sorted([dbs_dict[k][i] for k in dbs_dict for i in range(len(dbs_dict[k]))])


def decode_results(response, file_format, compressed):
    """Decodes the response from the UniProt API."""
    if compressed:
        decompressed = zlib.decompress(response.content, 16 + zlib.MAX_WBITS)
        if file_format == "json":
            j = json.loads(decompressed.decode("utf-8"))
            return j
        elif file_format == "tsv":
            return [line for line in decompressed.decode("utf-8").split("\n") if line]
        elif file_format == "xlsx":
            return [decompressed]
        elif file_format == "xml":
            return [decompressed.decode("utf-8")]
        else:
            return decompressed.decode("utf-8")
    elif file_format == "json":
        return response.json()
    elif file_format == "tsv":
        return [line for line in response.text.split("\n") if line]
    elif file_format == "xlsx":
        return [response.content]
    elif file_format == "xml":
        return [response.text]
    return response.text


def get_xml_namespace(element):
    """Get the namespace of an XML element."""
    m = re.match(r"\{(.*)\}", element.tag)
    return m.groups()[0] if m else ""


def print_progress_batches(batch_index, size, retrieved, failed):
    """Prints the progress of a batch process."""
    n_fetched = min((batch_index + 1) * size, retrieved)
    print(f"Fetched: {n_fetched} / {retrieved + failed}")


def divide_batches(ids):
    """Divides a list of UniProtIDs into batches of 500"""
    return [ids[i : i + 500] for i in range(0, len(ids), 500)]
