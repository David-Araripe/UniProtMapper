# -*- coding: utf-8 -*-
"""Module for mapping different identifiers through the id-mapping REST API."""

import json
from typing import List, Optional, Tuple, Union
from urllib.parse import parse_qs, urlencode, urlparse

import numpy as np
import pandas as pd
import pkg_resources

from .interface import abc_UniProtAPI
from .swiss_parser import SwissProtParser
from .utils import (
    decode_results,
    divide_batches,
    merge_xml_results,
    print_progress_batches,
)


class UniProtIDMapper(abc_UniProtAPI):
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
        super().__init__(
            pooling_interval,
            total_retries,
            backoff_factor,
            api_url,
        )
        self._mapping_dbs_path = pkg_resources.resource_filename(
            "UniProtMapper", "resources/uniprot_mapping_dbs.json"
        )

    def __call__(
        self,
        ids: Union[List[str], str],
        from_db: str = "UniProtKB_AC-ID",
        to_db: str = "UniProtKB-Swiss-Prot",
        parser: SwissProtParser = None,
    ) -> Tuple[pd.DataFrame, list]:
        """Wrapper for the `mapIDs` method.

        Map Uniprot identifiers to other databases.

        Args:
            ids: single id (str) or list of IDs to be mapped.
            from_db: original database from the `ids`. Defaults to "UniProtKB_AC-ID".
            to_db: identifier type to be obtained. Response is much more complex for
                "UniProtKB-Swiss-Prot". For this, see self.uniprot_swissprot_parser().
                Defaults to "UniProtKB-Swiss-Prot".
            parser: SwissProtParser object to parse the response. Defaults to None.

        Returns:
            Tuple[pd.DataFrame, list]. First element is a data frame with
            the mapping results. Second element is a list of failed IDs.
        """
        # __call__ is a wrapper to the uniprot_id_mapping function
        return self.mapIDs(ids, from_db=from_db, to_db=to_db, parser=parser)

    def _check_dbs(self, from_db, to_db):
        if from_db not in self._supported_dbs:
            print(
                "To types of supported databases, check the "
                '"supported_dbs_with_types" attribute.'
            )
            raise ValueError(
                f"{from_db} not available. "
                f"Supported databases are {self._supported_dbs}"
            )
        if to_db not in self._supported_dbs:
            print(
                "To types of supported databases, check the "
                '"supported_dbs_with_types" attribute.'
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
        failed = len(results.get("failedIds", []))
        if failed > 0:
            print(f"Failed to map {failed} ID(s).")
        retrieved = int(request.headers["x-total-results"])
        print_progress_batches(0, size, retrieved, failed)
        for i, batch in enumerate(self.get_batch(request, file_format, compressed), 1):
            results = self.combine_batches(results, batch, file_format)
            print_progress_batches(i, size, retrieved, failed)
        if file_format == "xml":
            return merge_xml_results(results)
        return results

    def mapIDs(
        self,
        ids: Union[List[str], str],
        from_db: str = "UniProtKB_AC-ID",
        to_db: str = "UniProtKB-Swiss-Prot",
        parser: SwissProtParser = None,
    ) -> Tuple[pd.DataFrame, list]:
        """Map Uniprot identifiers to other databases.

        Args:
            ids: single id (str) or list of IDs to be mapped.
            from_db: original database from the `ids`. Defaults to "UniProtKB_AC-ID".
            to_db: identifier type to be obtained. Response is much more complex for
                "UniProtKB-Swiss-Prot". For this, see self.uniprot_swissprot_parser().
                Defaults to "UniProtKB-Swiss-Prot".
            parser: SwissProtParser object to parse the response. Defaults to None.

        Returns:
            Tuple[pd.DataFrame, list]. First element is a data frame with
            the mapping results. Second element is a list of failed IDs.
        """
        self._check_dbs(from_db, to_db)
        if isinstance(ids, str):
            ids = [ids]

        def _get_results(
            ids,
            from_db=from_db,
            to_db=to_db,
            parser=parser,
        ):
            job_id = self.submit_id_mapping(from_db=from_db, to_db=to_db, ids=ids)
            if self.check_id_mapping_ready(job_id, from_db=from_db, to_db=to_db):
                link = self.get_id_mapping_results_link(job_id)
                r = self.get_id_mapping_results_search(link)
                if parser is not None:
                    assert (
                        to_db == "UniProtKB-Swiss-Prot"
                    ), "Only SwissProt can be parsed."
                    for result in r["results"]:
                        response = result.pop("to")
                        result.update(parser(response))
                r_dict = {idx: r["results"][idx] for idx in range(len(r["results"]))}
                results_df = pd.DataFrame.from_dict(r_dict, orient="index")
                if "failedIds" in r.keys():
                    failed_ids = r["failedIds"]
                else:
                    failed_ids = []
                return results_df, failed_ids

        if len(ids) > 500:  # The API only allows 500 ids per request
            batched_ids = divide_batches(ids)
            all_dfs = []
            failed_ids = []
            for batch in batched_ids:
                df, failed = _get_results(batch)
                all_dfs.append(df)
                failed_ids = failed_ids + failed
            df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
            return df, failed_ids
        else:
            return _get_results(ids)

    def uniprot_ids_to_orthologs(
        self,
        ids: Union[List[str], str],
        organism: Optional[List[str]] = None,
        uniprot_info: Optional[list] = None,
        crossref_dbs: Optional[list] = None,
        case: bool = False,
    ) -> Tuple[pd.DataFrame, dict]:
        """Get orthologs from UniProt IDs by mapping to OrthoDB and back to
        UniProtKB-Swiss-Prot.

        Args:
            ids: single id (str) or list of IDs to be mapped.
            organism: used to query the resulting dataframe for the species. If set
                to None, all species will be returned. Defaults to None.
            uniprot_info: information to be retrieved from UniProtKB-Swiss-Prot.
                If None, all supported fields are retrieved. Defaults to None.
            crossref_dbs: retrieve info from cross-referenced databases. If none, won't
                return any. Supported dbs in `SwissProtParser._supported_crossrefs`.
                Defaults to None.
            case: case sensitivity for organism query. Defaults to False.

        Raises:
            ValueError: if organism is not a string or a list of strings.

        Returns:
            Tuple[pd.DataFrame, list]: a tuple with the resulting dataframe and a list.
        """
        if organism is not None:
            if isinstance(organism, str):
                pass
            elif isinstance(organism, list):
                organism = "|".join(organism)
            else:
                raise ValueError("organism must be a string or a list of strings.")

        case = case
        to_ortho_r, failed_r = self.uniprot_id_mapping(ids, to_db="OrthoDB")

        ortho_mapping = {
            to_ortho_r[idx]["to"]: to_ortho_r[idx]["from"]
            for idx in range(len(to_ortho_r))
        }

        ortho_ids = [to_ortho_r[k]["to"] for k in to_ortho_r]
        parser = SwissProtParser(toquery=uniprot_info, crossrefs=crossref_dbs)
        ortho_r, failed_r = self.uniprot_id_mapping(
            ortho_ids, from_db="OrthoDB", parser=parser
        )
        for idx in ortho_r.keys():
            ortho_r[idx].update({"orthodb_id": ortho_r[idx]["from"]})
            ortho_r[idx].update({"original_id": ortho_mapping[ortho_r[idx]["from"]]})
        parsed_df = pd.DataFrame.from_dict(ortho_r, orient="index")

        if organism is not None:
            parsed_df = parsed_df.query(
                "organism.str.contains(@organism, regex=True, case=@case)"
            ).reset_index(drop=True)

        queried_arr = np.array(ids)
        retrieved = parsed_df["original_id"].unique()
        failed = np.compress(~np.isin(queried_arr, retrieved), queried_arr).tolist()
        return parsed_df, failed
