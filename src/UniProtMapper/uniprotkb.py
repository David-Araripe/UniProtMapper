import re

import requests
from requests.adapters import HTTPAdapter, Retry


class SimpleField:
    """Simple field query. Used for fields like accession, protein_name, etc"""

    def __init__(self, field_name: str, field_value: str) -> None:
        self.field_name = field_name
        self.field_value = field_value

    def __repr__(self):
        return f"{self.field_name}:{self.field_value}"


class QuoteField:
    """Same as SimpleField but it quotes the value. Used for species, for example"""

    def __init__(self, field_name: str, field_value: str) -> None:
        self.field_name = field_name
        self.field_value = field_value

    def __repr__(self):
        return f"{self.field_name}:'{self.field_value}'"


class DateRangeField:
    """Field for date ranges. If desired, the date can be set to '*' to fetch until most recent."""

    def __init__(self, field_name: str, init_date: str, final_date) -> None:
        self.field_name = field_name
        self.init_date = self._format_checker(init_date, date_type="Initial")
        self.final_date = self._format_checker(final_date, date_type="Final")

    def _format_checker(self, date: str, date_type: str) -> str:
        if not re.match(r"\d{4}-\d{2}-\d{2}", date) and date != "*":
            raise ValueError(
                f"{date_type} in the incorrect format. Make sure to have it as YYYY-MM-DD"
            )
        return date

    def __repr__(self):
        return f"{self.field_name}:[{self.init_date} TO {self.final_date}]"


class RangeField:
    """Field for ranges. If desired, numbers can be set to * to fetch until 0 or infinity"""

    def __init__(self, field_name: str, init_value: str, final_value: str) -> None:
        self.field_name = field_name
        self.init_value = self._format_checker(init_value, value_type="Initial")
        self.final_value = self._format_checker(final_value, value_type="Final")

    def _format_checker(self, value: str, value_type: str) -> str:
        if not re.match(r"\d+", value) and value != "*":
            raise ValueError(
                f"{value_type} in the incorrect format. Make sure to have it as a number"
            )
        return value

    def __repr__(self):
        return f"{self.field_name}:[{self.init_value} TO {self.final_value}]"


class QueryBuilder:
    """Query builder for UniProt KB queries. Python bitwise operators (`&`, `|`, `~`)
    )can be used to combine queries."""

    def __init__(self, query: list) -> None:
        self.query = query

    def __and__(self, other):
        return QueryBuilder(self.query + ["AND"] + other.query)

    def __or__(self, other):
        return QueryBuilder(self.query + ["OR"] + other.query)

    def __invert__(self):
        return QueryBuilder(["NOT"] + self.query)

    def __repr__(self):
        return " ".join([str(q) for q in self.query])


class UniProtKBWrapper:

    def __init__(
        self,
        pooling_interval=3,
        total_retries=5,
        backoff_factor=0.25,
        api_url="https://rest.uniprot.org",
    ) -> None:
        self._API_URL = api_url
        self._POLLING_INTERVAL = pooling_interval
        self.retries = self._setup_retries(total_retries, backoff_factor)
        self.session = requests.Session()
        self._setup_session()

    def _setup_retries(self, total_retries, backoff_factor) -> None:
        return Retry(
            total=total_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[500, 502, 503, 504],
        )

    def _setup_session(self) -> None:
        self.session.mount("https://", HTTPAdapter(max_retries=self.retries))

    @property
    def allowed_fields(self) -> list:
        return [
            "accession",
            "active",
            "lit_author",
            "protein_name",
            "chebi",
            "xrefcount_pdb",
            "date_created",
            "date_modified",
            "date_sequence_modified",
            "database",
            "xref",
            "ec",
            "existence",
            "family",
            "fragment",
            "gene",
            "gene_exact",
            "go",
            "virus_host_name",
            "virus_host_id",
            "accession_id",
            "inchikey",
            "protein_name",
            "interactor",
            "keyword",
            "length",
            "mass",
            "cc_mass_spectrometry",
            "protein_name",
            "organelle",
            "organism_name",
            "organism_id",
            "plasmid",
            "proteome",
            "proteomecomponent",
            "sec_acc",
            "reviewed",
            "scope",
            "sequence",
            "strain",
            "taxonomy_name",
            "taxonomy_id",
            "tissue",
            "cc_webresource",
        ]

    def query_builder(self, query: list[dict, str]) -> str:

        return query

    def _set_params(self, **kwargs) -> dict:

        pass
