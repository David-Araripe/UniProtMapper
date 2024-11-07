"""Contain all the fields used by the UniProtKB api"""

from .field_base_classes import (
    BooleanField,
    DateRangeField,
    QuoteField,
    RangeField,
    SimpleField,
    XRefCountField,
)

# Boolean Fields


class Active(BooleanField):
    def __init__(self, field_value: bool) -> None:
        super().__init__("active", field_value)


class Fragment(BooleanField):
    def __init__(self, field_value: bool) -> None:
        super().__init__("fragment", field_value)


class Reviewed(BooleanField):
    """Boolean field. Whether the protein is reviewed or not"""

    def __init__(self, field_value: bool) -> None:
        super().__init__("reviewed", field_value)


class IsIsoform(BooleanField):
    def __init__(self, field_value: bool) -> None:
        super().__init__("is_isoform", field_value)


# Quote Fields


class ProteinName(QuoteField):
    def __init__(self, field_value: str) -> None:
        super().__init__("protein_name", field_value)


class OrganismName(QuoteField):
    def __init__(self, field_value: str) -> None:
        super().__init__("organism_name", field_value)


# Date Range Fields


class DateCreated(DateRangeField):
    def __init__(self, from_date: str, to_date: str) -> None:
        super().__init__("date_created", from_date, to_date)


class DateModified(DateRangeField):
    def __init__(self, from_date: str, to_date: str) -> None:
        super().__init__("date_modified", from_date, to_date)


class DateSequenceModified(DateRangeField):
    def __init__(self, from_date: str, to_date: str) -> None:
        super().__init__("date_sequence_modified", from_date, to_date)


# Range Fields


class Length(RangeField):
    def __init__(self, from_value: int, to_value: int) -> None:
        super().__init__("length", from_value, to_value)


class Mass(RangeField):
    def __init__(self, from_value: int, to_value: int) -> None:
        super().__init__("mass", from_value, to_value)


# XRefCount Field


class XRefCount(XRefCountField):
    def __init__(self, field_name, from_value: int, to_value: int) -> None:
        super().__init__(field_name, from_value, to_value)


# SimpleField classes


class Accession(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("accession", field_value)


class LitAuthor(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("lit_author", field_value)


class Chebi(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("chebi", field_value)


class Database(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("database", field_value)


class Xref(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("xref", field_value)


class Ec(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("ec", field_value)


class Existence(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("existence", field_value)


class Family(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("family", field_value)


class Gene(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("gene", field_value)


class GeneExact(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("gene_exact", field_value)


class Go(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("go", field_value)


class VirusHostName(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("virus_host_name", field_value)


class VirusHostId(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("virus_host_id", field_value)


class AccessionId(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("accession_id", field_value)


class Inchikey(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("inchikey", field_value)


class Interactor(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("interactor", field_value)


class Keyword(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("keyword", field_value)


class CcMassSpectrometry(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("cc_mass_spectrometry", field_value)


class Organelle(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("organelle", field_value)


class OrganismId(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("organism_id", field_value)


class Plasmid(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("plasmid", field_value)


class Proteome(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("proteome", field_value)


class Proteomecomponent(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("proteomecomponent", field_value)


class SecAcc(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("sec_acc", field_value)


class Scope(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("scope", field_value)


class TaxonomyName(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("taxonomy_name", field_value)


class TaxonomyId(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("taxonomy_id", field_value)


class Tissue(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("tissue", field_value)


class CcWebresource(SimpleField):
    def __init__(self, field_value: str) -> None:
        super().__init__("cc_webresource", field_value)
