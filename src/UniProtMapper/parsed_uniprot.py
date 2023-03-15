# -*- coding: utf-8 -*-
"""TODO: add module documentation"""

from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import pkg_resources
import requests

from UniProtMapper.interface import UniProtAPI
from UniProtMapper.utils import decode_results, divide_batches, print_progress_batches

default_fields = (
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


class UniProtRetriever(UniProtAPI):
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
        """TODO"""
        super().__init__(
            pooling_interval,
            total_retries,
            backoff_factor,
            api_url,
        )

    @property
    def fieldsTable(self):
        csv_path = pkg_resources.resource_filename(
            "UniProtMapper", "resources/uniprot_return_fields.csv"
        )
        return pd.read_csv(csv_path)

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
        raise NotImplementedError("This method is not implemented yet")

    def get_id_mapping_results_search(
        self, fields: str, url: str, file_format: str, compressed: bool
    ):
        """Get the id mapping results from the UniProt API.

        Args:
            fields:
            url: _description_
            file_format: _description_
            compressed: _description_

        Returns:
            _description_
        """
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
        columns = ["From"] + fields.split(",")  # First value is the original ID
        results_df = pd.DataFrame(data=data, columns=columns)
        return results_df

    def uniprot_id_mapping(  # TODO: rename this method
        self,
        ids: Union[List[str], str],
        fields: list = default_fields,
        from_db: str = "UniProtKB_AC-ID",
        file_format: str = "tsv",
        compressed: bool = False,
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
        fields = np.char.lower(np.array(fields))
        if not np.isin(fields, self.fieldsTable["Returned Field"]).all():
            raise ValueError(
                "Invalid fields. Valid fields are: "
                f"{self.fieldsTable['Returned Field'].values}"
            )
        fields = ",".join(fields)

        # TODO: check for the max size of 500 and divide the batches if needed
        if len(ids) > 500:
            divide_batches(ids)

        if isinstance(ids, str):
            ids = [ids]
        # Save query parameters to allow parsing of the response.
        self._ids = ids

        job_id = self.submit_id_mapping(from_db=from_db, to_db="UniProtKB", ids=ids)
        if self.check_id_mapping_results_ready(job_id):
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
