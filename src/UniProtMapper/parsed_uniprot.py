# -*- coding: utf-8 -*-

import json
import re
import time
from typing import List, Optional, Tuple, Union
from urllib.parse import parse_qs, urlencode, urlparse

import numpy as np
import pandas as pd
import pkg_resources
import requests
from requests.adapters import HTTPAdapter, Retry

from .swiss_parser import SwissProtParser
from .utils import decode_results, merge_xml_results, print_progress_batches

"""
The main module for the UniProtMapper package, with the main class and functions.

Several methods were either taken or adapted from the Python example for the
UniProt ID mapping RESTful API documentation. Source:
https://www.uniprot.org/help/id_mapping#submitting-an-id-mapping-job

Disclaimer: This is not an official UniProt package.

TODO: Also add suport for other programatic access, such as in:
https://www.uniprot.org/help/api_queries

# I would like to do this by implementing the functions from
# https://github.com/noatgnu/UniprotWebParser
"""

default_columns = (
    "accession,id,gene_names,protein_name,"
    "organism_name,organism_id,length,xref_refseq,"
    "go_id,go_p,go_c,go_f,cc_subcellular_location,"
    "ft_topo_dom,ft_carbohyd,mass,cc_mass_spectrometry,"
    "sequence,ft_var_seq,cc_alternative_products"
)


class UniProtRetriever:
    """Class for mapping UniProt IDs to other databases.

    Returns:
        dict: A dictionary with the results of the mapping.

    Example:
    >>> uni_mapping = UniProtMapper()
    >>> result = uni_mapping(uprot_ids, to_db='PDB')
    """

    def __init__(
        self,
        pooling_interval=3,
        total_retries=5,
        backoff_factor=0.25,
        api_url="https://rest.uniprot.org",
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
        self._mapping_dbs_path = pkg_resources.resource_filename(
            "UniProtMapper", "resources/uniprot_mapping_dbs.json"
        )
        # use these to implement parsing methods for the response.
        self._ids = None
        self._todb = None
        self._fromdb = None
        self.results = None

    def __call__(
        self,
        ids: Union[List[str], str],
        format: str = "txv",
    ) -> Tuple[dict[dict], Optional[list]]:
        """
        Wrapper for the UniProt ID mapping API.

        Args:
            ids: single id (str) or list of IDs to be mapped.
            from_db: Original database from the `ids`. Defaults to "UniProtKB_AC-ID".
            to_db: Database to retrieve information from.
                Defaults to "UniProtKB-Swiss-Prot".
            get_format: The format of the returned value. Defaults to 'csv'.
            parser: SwissProtParser object to parse the response. Defaults to None.

        Returns:
            Tuple[dict[dict], Optional[list]]. The first element is a dictionary
            with the results of the mapping. The second element is a list of ids
            that failed to be mapped.
        """
        pass
        # __call__ is a wrapper to the uniprot_id_mapping function
        # return self.uniprot_id_mapping(ids, from_db=from_db, to_db=to_db)

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

    def submit_id_mapping(self, ids):
        request = requests.post(
            f"{self._API_URL}/idmapping/run",
            data={
                "ids": ",".join(ids),
                "from": "UniProtKB_AC-ID",
                "to": "UniProtKB-Swiss-Prot",
            },
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
                try:
                    ready = bool(j["results"] or j["failedIds"])
                except KeyError:
                    raise requests.RequestException(
                        f"Unexpected response from {self._fromdb} to {self._todb}.\n"
                        'request.json() missing "results" and "failedIds"'
                    )
                return ready

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
        # parsed = urlparse(url)
        # query = parse_qs(parsed.query)
        # file_format = query["format"][0] if "format" in query else "json"
        # if "size" in query:
        #     size = int(query["size"][0])
        # else:
        #     size = 500
        #     query["size"] = size
        # compressed = (
        #     query["compressed"][0].lower() == "true" if "compressed" in query else False
        # )
        # parsed = parsed._replace(query=urlencode(query, doseq=True))
        # url = parsed.geturl()
        request = self.session.get(url, allow_redirects=False)
        self.check_response(request)
        base_dict = {
            "format": "tsv",  # TODO: make this a parameter
            "fields": default_columns,
            "includeIsoform": "false",
            "size": 500,
        }
        results = requests.get(url + "/", params=base_dict)
        # print(dat.text)
        # results = decode_results(request, file_format, compressed)
        # failed = len(results.json().get("failedIds", []))
        # if failed > 0:
        #     print(f"Failed to map {failed} ID(s).")
        # retrieved = int(request.headers["x-total-results"])
        # print_progress_batches(0, size, retrieved, failed) # TODO: Implement this
        # for i, batch in enumerate(self.get_batch(request, file_format, compressed), 1):
        #     results = self.combine_batches(results, batch, file_format)
        #     print_progress_batches(i, size, retrieved, failed)
        # if file_format == "xml":
        #     return merge_xml_results(results)
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
        ids: Union[List[str], str],
    ) -> Tuple[dict[dict], Optional[list]]:
        """Map Uniprot identifiers to other databases.

        Args:
            ids: single id (str) or list of IDs to be mapped.
            from_db: original database from the `ids`. Defaults to "UniProtKB_AC-ID".
            to_db: identifier type to be obtained. Response is much more complex for
                "UniProtKB-Swiss-Prot". For this, see self.uniprot_swissprot_parser().
                Defaults to "UniProtKB-Swiss-Prot".
            parser: SwissProtParser object to parse the response. Defaults to None.

        Returns:
            Tuple[dict[dict], Optional[list]]. First element is a dictionary with
            the mapping results. Second element is a list of failed IDs.

        To convert results into a dataframe, use:
        >>> pd.DataFrame.from_dict(<returned value>, orient='index')
        """
        if isinstance(ids, str):
            ids = [ids]
        # Save query parameters to allow parsing of the response.
        self._ids = ids

        job_id = self.submit_id_mapping(ids=ids)
        if self.check_id_mapping_results_ready(job_id):
            link = self.get_id_mapping_results_link(job_id)
            r = self.get_id_mapping_results_search(link)
            return r.text
            # r_dict = {idx: r["results"][idx] for idx in range(len(r["results"]))}
            # if "failedIds" in r.keys():
            #     failed_r = r["failedIds"]
            # else:
            #     failed_r = None
            # self.results = r_dict
            # return r_dict, failed_r
