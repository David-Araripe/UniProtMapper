# -*- coding: utf-8 -*-
"""Holds UniProtRetriever: a class for returning specific fields from UniProt. For
a list of all supported fields, see https://www.uniprot.org/help/return_fields. 

Supported fields also stored as a dataframe in the `fields_table` attribute.
"""

import json
from typing import List, Tuple, Union

import numpy as np
import pandas as pd
import pkg_resources
import requests

from UniProtMapper.interface import abc_UniProtAPI
from UniProtMapper.utils import decode_results, divide_batches, print_progress_batches


class UniProtRetriever(abc_UniProtAPI):
    """Class for retrieving specific UniProt fields.

    Returns:
        Tuple[pd.DataFrame, list]: A tuple containing a dataframe with the results
        and a list of IDs that were not found.

    Example:
    >>> uni_retriever = UniProtRetriever()
    >>> result_df, failed = uni_retriever(["P30542", "Q16678", "Q02880"],
    >>>                                   fields=["accession", "id", "go_id",
    >>>                                           "go_p", "go_c", "go_f"])
    """

    def __init__(
        self,
        pooling_interval=3,
        total_retries=5,
        backoff_factor=0.25,
        api_url="https://rest.uniprot.org",
    ) -> None:
        """Initialize the class. This will set up the session and retry mechanism.

        Args:
            pooling_interval: The interval in seconds between polling the API.
                Defaults to 3.
            total_retries: The total number of retries to attempt. Defaults to 5.
            backoff_factor: The backoff factor to use when retrying. Defaults to 0.25.
            api_url: The url for the REST API. Defaults to "https://rest.uniprot.org".
        """
        super().__init__(
            pooling_interval,
            total_retries,
            backoff_factor,
            api_url,
        )
        self.default_fields = (
            "accession",
            "id",
            "gene_names",
            "protein_name",
            "organism_name",
            "organism_id",
            "go_id",
            "go_p",
            "go_c",
            "go_f",
            "cc_subcellular_location",
            "sequence",
        )

    @property
    def fields_table(self):
        csv_path = pkg_resources.resource_filename(
            "UniProtMapper", "resources/uniprot_return_fields.csv"
        )
        return pd.read_csv(csv_path)

    @property
    def _supported_dbs(self) -> list:
        """Only databases. There will be no information as to the type."""
        _mapping_dbs_path = pkg_resources.resource_filename(
            "UniProtMapper", "resources/uniprot_mapping_dbs.json"
        )
        with open(_mapping_dbs_path, "r") as f:
            dbs_dict = json.load(f)
        return sorted(
            [dbs_dict[k][i] for k in dbs_dict for i in range(len(dbs_dict[k]))]
        )

    def __call__(
        self,
        ids: Union[List[str], str],
        fields: list = None,
        from_db: str = "UniProtKB_AC-ID",
        to_db: str = "UniProtKB-Swiss-Prot",
        file_format: str = "tsv",
        compressed: bool = False,
    ) -> Tuple[pd.DataFrame, list]:
        """Wrapper for the `retrieveFields` method.

        Retrieves the requested fields from the UniProt ID Mapping API.
        Supported fields are listed in the `fields_table` attribute.

        Args:
            ids: list of IDs to be mapped or single string.
            fields: list of fields to be retrieved. Defaults to None.
            from_db: database for the ids. Defaults to "UniProtKB_AC-ID".
            to_db: UniProtDB to query to. For reviewed-only accessions, use default. If
                you want to include unreviewed accessions, use "UniProtKB". Defaults to
                "UniProtKB-Swiss-Prot".
            file_format: desired file format. Defaults to "tsv".
            compressed: compressed API request. Defaults to False.

        Raises:
            ValueError: If parameters `from_db`or `to_db` are not supported.

        Returns:
            Tuple[pd.DataFrame, list]: First element is a dataframe with the
            results, second element is a list of failed IDs.
        """
        return self.retrieveFields(ids, fields, from_db, to_db, file_format, compressed)

    def get_id_mapping_results_search(
        self, fields: str, url: str, file_format: str, compressed: bool
    ):
        """Get the id mapping results from the UniProt API."""
        assert file_format in ["json", "tsv", "xlsx", "xml"]
        query_dict = {
            "format": file_format,
            "fields": fields,
            "includeIsoform": "false",
            "size": 500,
            "compressed": {"true" if compressed else "false"},
        }
        self.check_response(self.session.get(url, allow_redirects=False))
        request = requests.get(url + "/", params=query_dict)
        results = decode_results(request, file_format, compressed=compressed)
        for i, batch in enumerate(self.get_batch(request, file_format, compressed), 1):
            results = self.combine_batches(results, batch, file_format)
        if file_format == "tsv":
            data = [d.split("\t") for d in results]
        else:
            raise NotImplementedError("Only tsv format is implemented")
        columns = data[0]
        results_df = pd.DataFrame(data=data[1:], columns=columns)
        return results_df

    def retrieveFields(
        self,
        ids: Union[List[str], str],
        fields: list = None,
        from_db: str = "UniProtKB_AC-ID",
        to_db: str = "UniProtKB-Swiss-Prot",
        file_format: str = "tsv",
        compressed: bool = False,
    ) -> Tuple[pd.DataFrame, list]:
        """Retrieves the requested fields from the UniProt ID Mapping API.
        Supported fields are listed in the `fields_table` attribute. For a complete
        list of the supported fields, check: https://www.uniprot.org/help/return_fields

        Args:
            ids: list of IDs to be mapped or single string.
            fields: list of fields to be retrieved. Defaults to None.
            from_db: database for the ids. Defaults to "UniProtKB_AC-ID".
            to_db: UniProtDB to query to. For reviewed-only accessions, use default. If
                you want to include unreviewed accessions, use "UniProtKB". Defaults to
                "UniProtKB-Swiss-Prot".
            file_format: desired file format. Defaults to "tsv".
            compressed: compressed API request. Defaults to False.

        Raises:
            ValueError: If parameters `from_db`or `to_db` are not supported.

        Returns:
            Tuple[pd.DataFrame, list]: First element is a dataframe with the
            results, second element is a list of failed IDs.
        """
        if from_db not in self._supported_dbs:
            raise ValueError(
                f"{from_db} not available. "
                f"Supported databases are {self._supported_dbs}"
            )
        if to_db not in ["UniProtKB-Swiss-Prot", "UniProtKB"]:
            raise ValueError(
                f"{to_db} not available. "
                "Supported databases are UniProtKB-Swiss-Prot and UniProtKB"
            )
        if isinstance(ids, str):
            ids = [ids]

        if fields is None:
            fields = self.default_fields
        else:
            fields = np.char.lower(np.array(fields))
            if not np.isin(fields, self.fields_table["Returned Field"]).all():
                raise ValueError(
                    "Invalid fields. Valid fields are: "
                    f"{self.fields_table['Returned Field'].values}"
                )
        fields = ",".join(fields)

        def _get_results(
            ids,
            fields=fields,
            from_db=from_db,
            to_db=to_db,
            file_format=file_format,
            compressed=compressed,
        ):
            job_id = self.submit_id_mapping(from_db=from_db, to_db=to_db, ids=ids)
            if self.check_id_mapping_ready(job_id, from_db=from_db, to_db=to_db):
                link = self.get_id_mapping_results_link(job_id)
                df = self.get_id_mapping_results_search(
                    fields, link, file_format, compressed
                )
                retrieved = len(df["From"].values)
                failed_arr = np.isin(ids, df["From"].values, invert=True)
                n_failed = failed_arr.astype(int).sum()
                failed_ids = np.compress(failed_arr, ids).tolist()
                print_progress_batches(0, 500, retrieved, n_failed)
                return df, failed_ids

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
