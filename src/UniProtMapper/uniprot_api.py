# -*- coding: utf-8 -*-

import json
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlparse

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter, Retry

from .utils import (
    decode_results,
    flatten_list_getunique,
    merge_xml_results,
    print_progress_batches,
    search_comments,
    search_keys_inlist,
    search_uniprot_crossrefs,
)

# Code source:
# https://www.uniprot.org/help/id_mapping#submitting-an-id-mapping-job


class UniProtMapper:
    """Class for mapping UniProt IDs to other databases.

    Returns:
        dict: A dictionary with the results of the mapping.

    Example:
    >>> uni_mapping = UniProtMapper()
    >>> result = uni_mapping(uprot_ids, to_db='PDB')
    """

    def __init__(
        self,
        api_url="https://rest.uniprot.org",
        pooling_interval=3,
        total_retries=5,
        backoff_factor=0.25,
    ) -> None:
        """Initialize the class.

        Args:
            api_url: The url for the REST API. Defaults to "https://rest.uniprot.org".
            pooling_interval: The interval in seconds between polling the API.
                Defaults to 3.
            total_retries: The total number of retries to attempt. Defaults to 5.
            backoff_factor: The backoff factor to use when retrying. Defaults to 0.25.
        """
        self._API_URL = api_url
        self._POLLING_INTERVAL = pooling_interval
        self.retries = self._setup_retries(total_retries, backoff_factor)
        self.session = requests.Session()
        self._setup_session()
        self._re_next_link = re.compile(r'<(.+)>; rel="next"')
        self._abbrev_dbs_path = (
            Path(__file__).absolute().parent / "uniprot_abbrev_crossrefs.json"
        )
        self._mapping_dbs_path = (
            Path(__file__).absolute().parent / "uniprot_mapping_dbs.json"
        )
        # use these to implement parsing methods for the response.
        self._todb = None
        self._fromdb = None
        self.results = None

    def __call__(
        self,
        ids: List[str],
        from_db: str = "UniProtKB_AC-ID",
        to_db: str = "UniProtKB-Swiss-Prot",
    ) -> Tuple[dict, Optional[list]]:
        """
        Wrapper for the UniProt ID mapping API.

        Args:
            ids: List of UniProt IDs.
            from_db: Original database from the `ids`. Defaults to "UniProtKB_AC-ID".
            to_db: Database to retrieve information from.
                Defaults to "UniProtKB-Swiss-Prot".
            get_format: The format of the returned value. Defaults to 'csv'.

        Returns:
            Tuple[dict, Optional[list]]
        """
        # __call__ is a wrapper to the uniprot_id_mapping function
        return self.uniprot_id_mapping(ids, from_db=from_db, to_db=to_db)

    def uniprot_ids_to_orthologs(
        self,
        ids: List[str],
        organism: Optional[List[str]] = None,
        case: bool = False,
    ) -> Tuple[pd.DataFrame, list]:
        case = case
        to_ortho_r, failed_r = self.uniprot_id_mapping(ids, to_db="OrthoDB")

        ortho_mapping = {
            to_ortho_r[idx]["to"]: to_ortho_r[idx]["from"]
            for idx in range(len(to_ortho_r))
        }

        ortho_ids = [to_ortho_r[k]["to"] for k in to_ortho_r]
        from_ortho_r, failed_r = self.uniprot_id_mapping(ortho_ids, from_db="OrthoDB")

        parsed_results = {}
        for idx in from_ortho_r.keys():
            parsed_r = self.uniprot_swissprot_parser(from_ortho_r[idx]["to"])
            parsed_r.update({"orthodb_id": from_ortho_r[idx]["from"]})
            parsed_r.update({"original_id": ortho_mapping[from_ortho_r[idx]["from"]]})
            parsed_results.update({idx: parsed_r})

        parsed_df = pd.DataFrame.from_dict(parsed_results, orient="index")

        if organism is not None:
            if isinstance(organism, str):
                pass
            elif isinstance(organism, list):
                organism = "|".join(organism)
            else:
                raise ValueError(f"organism must be a string or a list of strings.")
            parsed_df = parsed_df.query(
                f"organism.str.contains(@organism, regex=True, case=@case)"
            ).reset_index(drop=True)

        queried_arr = np.array(ids)
        retrieved = parsed_df["original_id"].unique()
        failed = np.compress(~np.isin(queried_arr, retrieved), queried_arr).tolist()

        return parsed_results, failed

    def _check_dbs(self, from_db, to_db):
        if from_db not in self._supported_dbs:
            print(
                'To types of supported databases, check the "supported_dbs_with_types" attribute.'
            )
            raise ValueError(
                f"{from_db} not available. "
                f"Supported databases are {self._supported_dbs}"
            )
        if to_db not in self._supported_dbs:
            print(
                'To types of supported databases, check the "supported_dbs_with_types" attribute.'
            )
            raise ValueError(
                f"{to_db} not available. "
                f"Supported databases are {self._supported_dbs}"
            )

    @property
    def supported_dbs_with_types(self) -> dict:
        """Available databases and their types for the UniProt ID mapping API.
        This function will return the full json file with the database types.
        json file obtained from https://www.uniprot.org/database?query=*"""
        with open(self._mapping_dbs_path, "r") as f:
            return json.load(f)

    @property
    def _supported_dbs(self) -> list:
        """Only databases. There will be no information as to the type."""
        dbs_dict = self.supported_dbs_with_types
        return sorted(
            [dbs_dict[k][i] for k in dbs_dict for i in range(len(dbs_dict[k]))]
        )

    @property
    def _supported_abbrev_dbs(self) -> list:
        """Abbreviations of the databases. Used to retrieve cross references
        from the UniProtKB-Swiss-Prot responses."""
        with open(self._abbrev_dbs_path, "r") as f:
            dbs_dict = json.load(f)
        return sorted(
            [dbs_dict["results"][i]["abbrev"] for i in range(len(dbs_dict["results"]))]
        )

    def _setup_retries(self, total_retries, backoff_factor) -> None:
        return Retry(
            total=total_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[500, 502, 503, 504],
        )

    def _setup_session(self) -> None:
        self.session.mount("https://", HTTPAdapter(max_retries=self.retries))

    def check_response(self, response):
        try:
            response.raise_for_status()
        except requests.HTTPError:
            print(response.json())
            raise

    def submit_id_mapping(self, from_db, to_db, ids):
        request = requests.post(
            f"{self._API_URL}/idmapping/run",
            data={"from": from_db, "to": to_db, "ids": ",".join(ids)},
        )
        self.check_response(request)
        return request.json()["jobId"]

    def get_next_link(self, headers):
        if "Link" in headers:
            match = self._re_next_link.match(headers["Link"])
            if match:
                return match.group(1)

    def check_id_mapping_results_ready(self, job_id):
        while True:
            request = self.session.get(f"{self._API_URL}/idmapping/status/{job_id}")
            self.check_response(request)
            j = request.json()
            if "jobStatus" in j:
                if j["jobStatus"] == "RUNNING":
                    print(f"Retrying in {self._POLLING_INTERVAL}s")
                    time.sleep(self._POLLING_INTERVAL)
                else:
                    raise Exception(j["jobStatus"])
            else:
                return bool(j["results"] or j["failedIds"])

    def get_batch(self, batch_response, file_format, compressed):
        batch_url = self.get_next_link(batch_response.headers)
        while batch_url:
            batch_response = self.session.get(batch_url)
            batch_response.raise_for_status()
            yield decode_results(batch_response, file_format, compressed)
            batch_url = self.get_next_link(batch_response.headers)

    def combine_batches(self, all_results, batch_results, file_format):
        if file_format == "json":
            for key in ("results", "failedIds"):
                if key in batch_results and batch_results[key]:
                    all_results[key] += batch_results[key]
        elif file_format == "tsv":
            return all_results + batch_results[1:]
        else:
            return all_results + batch_results
        return all_results

    def get_id_mapping_results_link(self, job_id):
        url = f"{self._API_URL}/idmapping/details/{job_id}"
        request = self.session.get(url)
        self.check_response(request)
        return request.json()["redirectURL"]

    def get_id_mapping_results_search(self, url):
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        file_format = query["format"][0] if "format" in query else "json"
        if "size" in query:
            size = int(query["size"][0])
        else:
            size = 500
            query["size"] = size
        compressed = (
            query["compressed"][0].lower() == "true" if "compressed" in query else False
        )
        parsed = parsed._replace(query=urlencode(query, doseq=True))
        url = parsed.geturl()
        request = self.session.get(url)
        self.check_response(request)
        results = decode_results(request, file_format, compressed)
        total = int(request.headers["x-total-results"])
        print_progress_batches(0, size, total)
        for i, batch in enumerate(self.get_batch(request, file_format, compressed), 1):
            results = self.combine_batches(results, batch, file_format)
            print_progress_batches(i, size, total)
        if file_format == "xml":
            return merge_xml_results(results)
        return results

    def get_id_mapping_results_stream(self, url):
        if "/stream/" not in url:
            url = url.replace("/results/", "/results/stream/")
        request = self.session.get(url)
        self.check_response(request)
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        file_format = query["format"][0] if "format" in query else "json"
        compressed = (
            query["compressed"][0].lower() == "true" if "compressed" in query else False
        )
        return decode_results(request, file_format, compressed)

    def uniprot_id_mapping(
        self,
        ids: List[str],
        from_db: str = "UniProtKB_AC-ID",
        to_db: str = "UniProtKB-Swiss-Prot",
    ):
        """
        Function to map Uniprot identifiers into other databases.
        Returns dictionary with query ids as keys and the respective
        mapped identifications.

        Args:
            ids: list of uniprot accession IDs to be mapped.
                (can be changed for querying other identifiers).
            from_db: identifier type of the `ids`.
            to_db: identifier type to be obtained.
            species: list of species you want to get data from.
                    Scientific name of species should be used.
                    Can used `all` to retrieve everything.

            Function currently used to map:
            >>> from_db='UniProtKB_AC-ID', to_db=('PDB' | 'Ensembl' | 'GeneID' | 'ChEMBL')
            >>> from_db='Gene_Name', to_db='UniProtKB-Swiss-Prot'
        """
        self._check_dbs(from_db, to_db)
        # Save query parameters to allow parsing of the response.
        self._todb = to_db
        self._fromdb = from_db

        job_id = self.submit_id_mapping(from_db=from_db, to_db=to_db, ids=ids)
        if self.check_id_mapping_results_ready(job_id):
            link = self.get_id_mapping_results_link(job_id)
            r = self.get_id_mapping_results_search(link)
            r_dict = {idx: r["results"][idx] for idx in range(len(r["results"]))}
            if "failedIds" in r.keys():
                failed_r = r["failedIds"]
            else:
                failed_r = None
            self.results = r_dict
            return r_dict, failed_r

    def uniprot_swissprot_parser(
        self,
        json_r=None,
        include_crossrefs: list = ["TCDB", "GO", "PRO"],
    ) -> dict:
        """
        Function to parse the json_r object returned from uniprot_id_mapping
        and to retrieve a defined set of information from the results.

        Args:
            json_r: json_r object returned from uniprot_id_mapping.
            include_crossrefs: UniProt cross references to be fetched.
                returned keyname will be `f'{ID}_crossref'.
                Defaults to ["TCDB", "GO", "PRO"].

        Returns:
            Dictionary with the information of the target.
        """
        include_crossrefs = np.array(include_crossrefs)
        if not np.isin(include_crossrefs, self._supported_abbrev_dbs).all():
            raise ValueError(
                f"include_crossrefs must be in {self._supported_abbrev_dbs}"
            )
        if self._todb != "UniProtKB-Swiss-Prot":
            raise ValueError(
                "uniprot_swissprot_parser only parses UniProtKB-Swiss-Prot responses"
            )
        d = defaultdict(str)
        if json_r is None:
            json_r = self.results
        d.update(json_r)

        accession = d["primaryAccession"]
        organism = d["organism"]["scientificName"]
        namekeys = d["proteinDescription"].keys()
        # Some UniProt entries have only submissionNames but no recommendedName
        # see as examples: 'Q72547', 'A1Z199', 'Q91ZM7', 'Q9YQ12'
        if "recommendedName" in namekeys:
            fullname = d["proteinDescription"]["recommendedName"]["fullName"]["value"]
        elif "submissionNames" in namekeys:
            fullname = d["proteinDescription"]["submissionNames"][0]["fullName"][
                "value"
            ]
        else:
            fullname = ""

        comment = search_comments(d["comments"], "DISEASE")
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

        # shortName might be found under different keys
        descriptions = d["proteinDescription"].keys()
        shortname = ""
        if "recommendedName" in descriptions:
            avail_names = d["proteinDescription"]["recommendedName"].keys()
            if "shortNames" in avail_names:
                shortname = d["proteinDescription"]["recommendedName"]["shortNames"][0][
                    "value"
                ]
        if ("alternativeNames" in descriptions) and (shortname == ""):
            shortname = search_keys_inlist(
                d["proteinDescription"]["alternativeNames"], "shortNames"
            )
            if shortname != "":
                shortname = shortname[0]["value"]

        if "genes" in d.keys():
            genename = search_keys_inlist(d["genes"], "geneName")
            genename = genename["value"] if genename != "" else ""
        else:
            genename = ""

        tissue_specif = search_comments(d["comments"], "TISSUE SPECIFICITY")
        if tissue_specif != "":
            tissue_specif = tissue_specif["texts"][0]["value"]

        prot_function = search_comments(d["comments"], "FUNCTION")
        if prot_function != "":
            # Check this won't raise errors
            prot_function = prot_function["texts"][0]["value"]

        # adding TCDB cross references if available - contains the protein function
        crossrefs = search_uniprot_crossrefs(d, include_crossrefs)

        sequence = d["sequence"]["value"]
        cell_location = search_comments(d["comments"], "SUBCELLULAR LOCATION")
        if cell_location != "":
            cell_location = cell_location["subcellularLocations"]
            cell_location = flatten_list_getunique(
                [
                    cell_location[x]["location"]["value"].split(", ")
                    for x in range(len(cell_location))
                ]
            )

        target_info_dict = {
            "accession": accession,
            "organism": organism,
            "fullName": fullname,
            "disease": disease,
            "disease_descr": disease_desc,
            "shortName": shortname,
            "geneName": genename,
            "tissueExpression": tissue_specif,
            "cellLocation": cell_location,
            "sequence": sequence,
            "function": prot_function,
        }
        target_info_dict.update(
            {f"{key}_crossref": value for key, value in crossrefs.items()}
        )
        return target_info_dict
