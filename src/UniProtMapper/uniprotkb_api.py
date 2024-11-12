"""Hold the class to interact with the UniProtKB API. For query construction, use the
field classes found in `UniProtMapper.uniprotkb_fields`."""

from logging import info
from typing import Generator, Optional, Union

import pandas as pd
import requests
from tqdm import tqdm

from .field_base_classes import QueryBuilder
from .interface import BaseUniProt


class ProtKB(BaseUniProt):

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

    def _build_search_url(
        self,
        query: str,
        fields: list[str],
        format: str = "tsv",
        include_isoform: bool = False,
        compressed: bool = False,
        size: int = 500,
    ) -> str:
        """Build the search URL with the given parameters.

        Args:
            query: Search query string
            fields: List of fields to retrieve
            format: Format of the response
            include_isoform: Whether to include isoforms
            compressed: Whether to request compressed response
            size: Batch size for pagination

        Returns:
            Complete URL for the API request
        """
        params = {
            "query": query,
            "fields": ",".join(fields),
            "format": format,
            "includeIsoform": str(include_isoform).lower(),
            "compressed": str(compressed).lower(),
            "size": size,
        }

        param_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self._API_URL}/uniprotkb/search?{param_string}"

    def submit_query(
        self,
        query: str,
        fields: list = None,
        include_isoform: bool = False,
        compressed: bool = True,
        format: str = "tab",
        size: int = 500,
    ) -> dict:
        request = requests.post(
            f"{self._API_URL}/uniprotkb/search?",
            data={
                "query": query,
                "fields": fields,
                "includeIsoform": str(include_isoform).lower(),
                "format": format,
                "size": size,
                "compressed": str(compressed).lower(),
            },
        )
        self.check_response(request)
        return request.json()["jobId"]

    @property
    def available_formats(self) -> list:
        return [
            "json",
            "xml",
            "txt",
            "list",
            "tsv",
            "fasta",
            "gff",
            "obo",
            "rdf",
            "xlsx",
        ]

    def _get_batches(
        self, initial_response
    ) -> Generator[tuple[requests.Response, int], None, None]:
        """Generator that yields batches of results with pagination.

        Args:
            initial_response: Initial response from the API

        Yields:
            Tuple containing:
                - Response object for the current batch
                - Total number of results
        """
        response = initial_response
        total = int(response.headers.get("x-total-results", 0))

        while True:
            yield response, total

            next_link = self.get_next_link(response.headers)
            if not next_link:
                break

            response = self.session.get(next_link)
            self.check_response(response)

    def get(
        self,
        query: Union[QueryBuilder, str],
        fields: Optional[list[str]] = None,
        format: str = "tsv",
        include_isoform: bool = False,
        compressed: bool = False,
        size: int = 500,
    ) -> pd.DataFrame:
        """Main method to retrieve data from UniProtKB. For the query, use the supported fields
        found within `UniProtMapper.uniprot_kb_fields`.

        An example of this would be:

        Args:
            fields: string or QueryBuilder object with the fields to retrieve.
            format: Format of the response. Defaults to "tsv"
            include_isoform: Whether to include isoforms. Defaults to False
            compressed: Whether to request compressed response. Defaults to False
            size: Batch size for pagination. Defaults to 500

        Returns:
            - DataFrame with the retrieved data
        """
        if fields is None:
            info(
                f"No fields provided. Using default fields: {', '.join(self.default_fields)}"
            )
            fields = list(self.default_fields)

        url = self._build_search_url(
            query=(str(query) if isinstance(query, QueryBuilder) else query),
            fields=fields,
            format=format,
            include_isoform=include_isoform,
            compressed=compressed,
            size=size,
        )

        response = self.session.get(url)
        self.check_response(response)

        results = []
        total_results = int(response.headers.get("x-total-results", 0))

        pbar = tqdm(
            self._get_batches(response),
            desc="Fetching data",
            total=total_results // size + 1,
        )

        for batch_response, _ in pbar:
            if format == "tsv":
                batch_data = batch_response.text.splitlines()
                if results:
                    batch_data = batch_data[1:]
                results.extend(batch_data)
            else:
                batch_data = batch_response.json()
                if "results" in batch_data:
                    results.extend(batch_data["results"])

            pbar.set_postfix({"fetched": f"{len(results)-1}/{total_results}"})

        if format == "tsv":
            df = pd.read_csv(pd.io.common.StringIO("\n".join(results)), sep="\t")
        else:
            df = pd.DataFrame(results)

        return df
