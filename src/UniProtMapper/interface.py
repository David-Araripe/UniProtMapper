"""Holds the implementation of the base class for the UniProt id-mapping REST API."""

import re
from abc import ABC

import requests
from requests.adapters import HTTPAdapter, Retry

from .utils import read_fields_table

"""
Several methods were either taken or adapted from the Python example for the
UniProt ID mapping RESTful API documentation. The original code can be found at:
https://www.uniprot.org/help/id_mapping#submitting-an-id-mapping-job
"""


class BaseUniProt(ABC):
    """Base class for the UniProt rest APIs covered by this package:

    - BaseUniProt -> ProtMapper (ID mapping API)
    - BaseUniProt -> ProtKB (UniProtKB API)
    """

    fields_table = read_fields_table()
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

    def __init__(
        self,
        pooling_interval: int = 3,
        total_retries: int = 5,
        backoff_factor: float = 0.25,
        api_url: str = "https://rest.uniprot.org",
    ) -> None:
        """Initialize the class. This will set up the session and retry mechanism.

        Args:
            pooling_interval: The interval in seconds between polling the API.
                Defaults to 3.
            total_retries: The total number of retries to attempt. Defaults to 5.
            backoff_factor: The backoff factor to use when retrying. Defaults to 0.25.
            api_url: The url for the REST API. Defaults to "https://rest.uniprot.org".
        """
        self._API_URL = api_url
        self._POLLING_INTERVAL = pooling_interval
        self.retries = self._setup_retries(total_retries, backoff_factor)
        self.session = requests.Session()
        self._setup_session()
        self._re_next_link = re.compile(r'<(.+)>; rel="next"')
        self._cached_supported_return_fields = None

    @property
    def supported_return_fields(self) -> list:
        """Return a list of the supported fields in UniProtKB & ID mapping API."""
        if self._cached_supported_return_fields is None:
            full_version_fields = (
                self.fields_table.query('has_full_version == "yes"')["returned_field"]
                + "_full"
            ).tolist()
            self._cached_supported_return_fields = (
                self.fields_table["returned_field"].tolist() + full_version_fields
            )
        return self._cached_supported_return_fields

    def _setup_retries(self, total_retries, backoff_factor) -> None:
        return Retry(
            total=total_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[500, 502, 503, 504],
        )

    def _setup_session(self) -> None:
        self.session.mount("https://", HTTPAdapter(max_retries=self.retries))

    def check_response(self, response) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError:
            print(response.json())
            raise

    def get_next_link(self, headers) -> str:
        if "Link" in headers:
            match = self._re_next_link.match(headers["Link"])
            if match:
                return match.group(1)
