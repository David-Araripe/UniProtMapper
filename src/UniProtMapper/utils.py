# -*- coding: utf-8 -*-
import json
import re
import zlib
from xml.etree import ElementTree

import numpy as np


def search_keys_inlist(list_of_dicts, desiredkey):
    for diction in list_of_dicts:
        if desiredkey in diction:
            return diction[desiredkey]
    return ""


def search_comments(dict_comments, comment_type):
    """
    Function to search comment types within the uniprot json respose
    retrieved from `UniProtMapping.uniprot_id_mapping()` function
    """
    has_comment = False
    for i in dict_comments:
        if i["commentType"] == comment_type:
            has_comment = True
            r_value = i
            break
    if has_comment:
        return r_value
    else:
        return ""


def search_uniprot_crossrefs(uniprot_dict: dict, target_dbs: list):
    """Function to search a certain database within the dictionary
    retrieved from UniProt with the function `fetch_from_uniprot`.

    Args:
        uniprot_dict: Retrieved dictionary from UniProt.
        target_dbs: Database that you want to retrieve the information from.

    response will be retrieved in a dictionary with a key for each
    of the `target_dbs` and values as a list of strings with the forma:
    '`id`~properties[key]~properties[value]'
    """
    #
    to_retrieve = {t: [] for t in target_dbs}
    # This  will be iterating over a list of dictionaries
    for reference in uniprot_dict["uniProtKBCrossReferences"]:
        try:
            if reference["database"] in target_dbs:
                database = reference["database"]
                # Iterarting over a list of dictionaries again
                for prop in reference["properties"]:
                    to_retrieve[database].append(
                        f"{reference['id']}~{prop['key']}~{prop['value']}"
                    )
        except KeyError:
            continue
    return to_retrieve


def flatten_list_getunique(nested_list):
    """
    Flattens a list and returns the unique values
    """
    unflat = [element for sublist in nested_list for element in sublist]
    unflat_unique = list(np.unique(np.array(unflat)))
    return ", ".join(unflat_unique)

def decode_results(response, file_format, compressed):
    if compressed:
        decompressed = zlib.decompress(response.content, 16 + zlib.MAX_WBITS)
        if file_format == "json":
            j = json.loads(decompressed.decode("utf-8"))
            return j
        elif file_format == "tsv":
            return [
                line for line in decompressed.decode("utf-8").split("\n") if line
            ]
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
    m = re.match(r"\{(.*)\}", element.tag)
    return m.groups()[0] if m else ""

def merge_xml_results(xml_results):
    merged_root = ElementTree.fromstring(xml_results[0])
    for result in xml_results[1:]:
        root = ElementTree.fromstring(result)
        for child in root.findall("{http://uniprot.org/uniprot}entry"):
            merged_root.insert(-1, child)
    ElementTree.register_namespace(
        "", get_xml_namespace(merged_root[0])
    )
    return ElementTree.tostring(merged_root, encoding="utf-8", xml_declaration=True)

def print_progress_batches(batch_index, size, total):
    n_fetched = min((batch_index + 1) * size, total)
    print(f"Fetched: {n_fetched} / {total}")
        
