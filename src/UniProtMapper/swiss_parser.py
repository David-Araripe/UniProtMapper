# -*- coding: utf-8 -*-
import json
from collections import defaultdict

import numpy as np
import pkg_resources

from .utils import (
    flatten_list_getunique,
    search_comments,
    search_keys_inlist,
    search_uniprot_crossrefs,
)

"""
Module for parsing UniProtKB-Swiss-Prot json responses.
"""


class SwissProtParser:
    """Retrieve specified information UniProtKB-Swiss-Prot json response."""

    def __init__(self, toquery: list = None, crossrefs: list = None) -> None:
        """Initialize the class with the information to be retrieved
        and the crossreferences to be searched.

        Args:
            toquery: Fields annotated in UniProt. See supported in
                self._supported_fields(). Defaults to None.
            crossrefs: UniProt crossreferences to be retrieved.
                Defaults to None.
        """
        # Where the retrieved information will be stored
        self._crossrefs_path = pkg_resources.resource_filename(
            "UniProtMapper", "resources/uniprot_abbrev_crossrefs.json"
        )
        self.crossrefs = crossrefs
        self._check_support("crossrefs")
        self.toquery = self._supported_fields if toquery is None else toquery
        self._check_support("toquery")
        self.d = defaultdict(str)  # Where the information gets stored for parsing
        pass

    @property
    def _supported_fields(self):
        return [
            "accession",
            "organism",
            "fullName",
            "disease",
            "disease_descr",
            "shortName",
            "geneName",
            "tissueExpression",
            "cellLocation",
            "sequence",
            "function",
        ]

    @property
    def _supported_crossrefs(self):
        with open(self._crossrefs_path, "r") as f:
            dbs_dict = json.load(f)
        return sorted(
            [dbs_dict["results"][i]["abbrev"] for i in range(len(dbs_dict["results"]))]
        )

    def __call__(self, json_r) -> dict:
        return self.parse_response(json_r)

    def __repr__(self) -> str:
        return f"SwissProtParser(toquery={self.toquery}, crossrefs={self.crossrefs})"

    def _check_support(self, field: str) -> None:
        if field == "crossrefs":
            if self.crossrefs is None:
                return
            supported = np.array(self._supported_crossrefs)
            touse = np.array(self.crossrefs)
            if not np.isin(touse, supported).all():
                raise ValueError(f"Crossreferences must be specified to query {field}")
        if field == "toquery":
            supported = np.array(self._supported_fields)
            touse = np.array(self.toquery)
            if not np.isin(touse, supported).all():
                raise ValueError(f"Fields must be specified to query {field}")

    def parse_response(self, json_r) -> dict:
        self.d.update(json_r)
        filtered_dict = dict()

        if "accession" in self.toquery:
            filtered_dict.update({"accession": self._get_accession()})

        if "organism" in self.toquery:
            filtered_dict.update({"organism": self._get_organism()})

        if "fullName" in self.toquery:
            filtered_dict.update({"fullName": self._get_fullName()})

        if any(["disease" in self.toquery, "disease_descr" in self.toquery]):
            disease, disease_desc = self._get_disease_info()
            if "disease" in self.toquery:
                filtered_dict.update({"disease": disease})
            if "disease_descr" in self.toquery:
                filtered_dict.update({"disease_descr": disease_desc})

        if "shortName" in self.toquery:
            filtered_dict.update({"shortName": self._get_shortName()})

        if "geneName" in self.toquery:
            filtered_dict.update({"geneName": self._get_geneName()})

        if "tissueExpression" in self.toquery:
            filtered_dict.update({"tissueExpression": self._get_tissueExpression()})

        if "cellLocation" in self.toquery:
            filtered_dict.update({"cellLocation": self._get_cellLocation()})

        if "sequence" in self.toquery:
            filtered_dict.update({"sequence": self._get_sequence()})

        if "function" in self.toquery:
            filtered_dict.update({"function": self._get_function()})

        if self.crossrefs is not None:
            crossrefs = search_uniprot_crossrefs(self.d, self.crossrefs)
            filtered_dict.update(
                {f"{key}_crossref": value for key, value in crossrefs.items()}
            )
        self.d = defaultdict(str)
        return filtered_dict

    def _get_accession(self):
        return self.d["primaryAccession"]

    def _get_organism(self):
        return self.d["organism"]["scientificName"]

    def _get_fullName(self):
        namekeys = self.d["proteinDescription"].keys()
        # Some UniProt entries have only submissionNames but no recommendedName
        # see as examples: 'Q72547', 'A1Z199', 'Q91ZM7', 'Q9YQ12'
        if "recommendedName" in namekeys:
            fullname = self.d["proteinDescription"]["recommendedName"]["fullName"][
                "value"
            ]
        elif "submissionNames" in namekeys:
            fullname = self.d["proteinDescription"]["submissionNames"][0]["fullName"][
                "value"
            ]
        else:
            fullname = ""
        return fullname

    def _get_disease_info(self):
        comment = search_comments(self.d["comments"], "DISEASE")
        if comment != "":
            disease_info = comment.keys()
            # Sometimes there's no annotation for "disease", but only notes
            # For an example: Q02880
            if "disease" in disease_info:
                disease = comment["disease"].get("diseaseId", "")
                disease_desc = comment["disease"].get("description", "")
            else:
                disease = ""
                disease_desc = ""
        else:
            disease = ""
            disease_desc = ""
        return disease, disease_desc

    def _get_shortName(self):
        # shortName might be found under different keys
        descriptions = self.d["proteinDescription"].keys()
        shortname = ""
        if "recommendedName" in descriptions:
            avail_names = self.d["proteinDescription"]["recommendedName"].keys()
            if "shortNames" in avail_names:
                shortname = self.d["proteinDescription"]["recommendedName"][
                    "shortNames"
                ][0]["value"]
        if ("alternativeNames" in descriptions) and (shortname == ""):
            shortname = search_keys_inlist(
                self.d["proteinDescription"]["alternativeNames"], "shortNames"
            )
            if shortname != "":
                shortname = shortname[0]["value"]
        return shortname

    def _get_geneName(self):
        if "genes" in self.d.keys():
            genename = search_keys_inlist(self.d["genes"], "geneName")
            genename = genename["value"] if genename != "" else ""
        else:
            genename = ""
        return genename

    def _get_tissueExpression(self):
        tissue_specif = search_comments(self.d["comments"], "TISSUE SPECIFICITY")
        if tissue_specif != "":
            tissue_specif = tissue_specif["texts"][0]["value"]
        return tissue_specif

    def _get_cellLocation(self):
        cell_location = search_comments(self.d["comments"], "SUBCELLULAR LOCATION")
        if cell_location != "":
            cell_location = cell_location["subcellularLocations"]
            cell_location = flatten_list_getunique(
                [
                    cell_location[x]["location"]["value"].split(", ")
                    for x in range(len(cell_location))
                ]
            )
        return cell_location

    def _get_sequence(self):
        return self.d["sequence"]["value"]

    def _get_function(self):
        prot_function = search_comments(self.d["comments"], "FUNCTION")
        if prot_function != "":
            # Check this won't raise errors
            prot_function = prot_function["texts"][0]["value"]
        return prot_function

    def _get_crossrefs(self, uniprot_dict: dict, target_dbs: list):
        """Search crossreferences in the "UniProtKB-Swiss-Prot" json response.

        Args:
            json_r: json response from UniProtKB-Swiss-Prot.
            target_dbs: Database that you want to retrieve the information from.

        Returns:
            Dictionary with a key for each of the `target_dbs` and values as a list
            of strings formatted as: '`id`~properties[key]~properties[value]'
        """
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
