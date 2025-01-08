"""Contain all the fields used by the UniProtKB API wrapped as python classes compatible with
the following boolean operators:

- & : AND operation
- `|` : OR operation
- ~ : NOT operation

For a list of query fields on UniProt's website, refer to https://www.uniprot.org/help/query-fields
"""

from typing import Union

from .field_base_classes import (
    BooleanField,
    DateRangeField,
    QuoteField,
    RangeField,
    SimpleField,
    XRefCountField,
)

# Boolean Fields


class active(BooleanField):
    """Boolean field. If set to `False`, return obsolete entries"""

    def __init__(self, field_value: bool) -> None:
        """Initalize the `active` UniProtKB data field.

        Args:
            field_value: If set to `False`, return obsolete entries.
        """

        super().__init__("active", field_value)


class fragment(BooleanField):
    """Boolean field. If set to `True`, list entries with an incomplete sequence."""

    def __init__(self, field_value: bool) -> None:
        """Initalize the `fragment` UniProtKB data field.

        Args:
            field_value: If set to `True`, list entries with an incomplete sequence.
        """
        super().__init__("fragment", field_value)


class reviewed(BooleanField):
    """Boolean field. If set to `True`, return only reviewed entries"""

    def __init__(self, field_value: bool) -> None:
        """Initalize the `reviewed` UniProtKB data field.

        Args:
            field_value: If set to `True`, return only reviewed entries.
        """
        super().__init__("reviewed", field_value)


class is_isoform(BooleanField):
    """Boolean field. If set to `True`, return only isoform entries"""

    def __init__(self, field_value: bool) -> None:
        """Initalize the `is_isoform` UniProtKB data field.

        Args:
            field_value: If set to `True`, return only isoform entries.
        """
        super().__init__("is_isoform", field_value)


# Quote Fields


class protein_name(QuoteField):
    """Field for protein names. Further functionality:
    - Query for "name_1" while excluding "name_2",
    >>> protein_name('name_1 - name_2')

    - Query for "name_1" *and* "name_2", in this order,
    >>> protein_name('name_1 name_2')

    - Glob-like search for all entries with protein names starting with "anti":
    >>> protein_name('anti*')
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `protein_name` UniProtKB data field.

        Args:
            field_value: The protein name to search for.
        """
        super().__init__("protein_name", field_value)


class organism_name(QuoteField):
    """Field for organism names. Further functionality:
    - Query for "name_1" while excluding "name_2",
    >>> organism_name('name_1 - name_2')

    - Query for "name_1" *and* "name_2", in this order,
    >>> organism_name('name_1 name_2')

    - Glob-like search for all entries with organism names starting with "escherichia":
    >>> organism_name('escherichia*')

    For more information on the organism names, see: https://www.uniprot.org/taxonomy?query=*
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `organism_name` UniProtKB data field.

        Args:
            field_value: The organism name to search for.
        """
        super().__init__("organism_name", field_value)


# Date Range Fields


class date_created(DateRangeField):
    """Query entries created within a time range defined from dates. Date format: `YYYY-MM-DD`.

    `*` can also be used as a wildcard for the latest or the earliest/latest date."""

    def __init__(self, from_date: str, to_date: str) -> None:
        """Initalize the `date_created` UniProtKB data field.

        Args:
            from_date: Starting date as either * (for the earliest) or YYYY-MM-DD.
            to_date: Ending date as either * (for the latest) or YYYY-MM-DD.
        """
        super().__init__("date_created", from_date, to_date)


class date_modified(DateRangeField):
    """Query entries modified within a time range defined from dates. Date format: `YYYY-MM-DD`.

    `*` can also be used as a wildcard for the latest or the earliest/latest date."""

    def __init__(self, from_date: str, to_date: str) -> None:
        """Initalize the `date_modified` UniProtKB data field.

        Args:
            from_date: Starting date as either * (for the earliest) or YYYY-MM-DD.
            to_date: Ending date as either * (for the latest) or YYYY-MM-DD.
        """
        super().__init__("date_modified", from_date, to_date)


class date_sequence_modified(DateRangeField):
    """Query entries with sequence information modified within a time range defined from dates.
    Date format: `YYYY-MM-DD`.

    `*` can also be used as a wildcard for the latest or the earliest/latest date."""

    def __init__(self, from_date: str, to_date: str) -> None:
        """Initalize the `date_sequence_modified` UniProtKB data field.

        Args:
            from_date: Starting date as either * (for the earliest) or YYYY-MM-DD.
            to_date: Ending date as either * (for the latest) or YYYY-MM-DD.
        """
        super().__init__("date_sequence_modified", from_date, to_date)


# Range Fields


class length(RangeField):
    """Query entries with sequence length within a certain range.

    Arguments should be integers or the wildcard `*` for the maximum or minimum value.
    """

    def __init__(self, from_value: Union[int, str], to_value: Union[int, str]) -> None:
        """Initalize the `length` UniProtKB data field.

        Args:
            from_value: The minimum length of the sequence. * can be used as a wildcard for zero.
            to_value: The maximum length of the sequence. * can be used as a wildcard for infinity.
        """
        super().__init__("length", from_value, to_value)


class mass(RangeField):
    """Query entries with mass within a certain range.

    Arguments should be integersor the wildcard `*` for the maximum or minimum value."""

    def __init__(self, from_value: Union[int, str], to_value: Union[int, str]) -> None:
        """Initalize the `mass` UniProtKB data field.

        Args:
            from_value: The minimum mass of the sequence. * can be used as a wildcard for zero.
            to_value: The maximum mass of the sequence. * can be used as a wildcard for infinity.
        """
        super().__init__("mass", from_value, to_value)


# XRefCount Field


class xref_count(XRefCountField):
    """Query entries with a certain number of cross-references. All fields within
    `UniProtMapper.utils.read_fields_table()['returned_field']` are supported.

    E.g.: to query entries with 20 or more cross-references to "PDB", use:
    >>> xref_count('pdb', 20, '*')

    Or:
    >>> xref_count('xref_pdb', 20, '*')
    """

    def __init__(self, field_name, from_value: int, to_value: int) -> None:
        """Initalize the `xref_count` UniProtKB data field.

        Args:
            field_name: Name of the cross-reference field to query.
            from_value: Minimum number of cross-references. * can be used as wildcard for zero.
            to_value: Maximum number of cross-references. * can be used as wildcard for infinity.
        """
        super().__init__(field_name, from_value, to_value)


# SimpleField classes


class accession(SimpleField):
    """Query for entries with a certain UniProt accession key."""

    def __init__(self, field_value: str) -> None:
        """Initalize the `accession` UniProtKB data field.

        Args:
            field_value: The UniProt accession key to search for.
        """
        super().__init__("accession", field_value)


class lit_author(SimpleField):
    """Query for entries with at least one reference co-authored by the specified author.
    Extra functionalities include:
    - Query for "name_1" while excluding entries with "name_2" as co-author,
    >>> lit_author('name_1 - name_2')

    - Query for "name_1" *and* "name_2", in this order,
    >>> lit_author('name_1 name_2')

    - Glob-like search for all entries with author starting with a Cavad:
    >>> lit_author('Cavad*')
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `lit_author` UniProtKB data field.

        Args:
            field_value: The author name to search for.
        """
        super().__init__("lit_author", field_value)


class chebi(SimpleField):
    """Query for entries with a certain ChEBI identifier. For more information, check the
    following: https://www.uniprot.org/help/chemical_data_search"""

    def __init__(self, field_value: str) -> None:
        """Initialize the `chebi` UniProtKB data field.

        Args:
            field_value: The ChEBI identifier to search for.
        """
        super().__init__("chebi", field_value)


class database(SimpleField):
    """List all entries with a cross reference to a certain database"""

    def __init__(self, field_value: str) -> None:
        """Initialize the `database` UniProtKB data field.

        Args:
            field_value: The database to search for.
        """
        super().__init__("database", field_value)


class xref(SimpleField):
    """List all entries with a cross reference to a certain database. E.g. of extra functionality:

    - Query all entries with a cross-reference to the PDB database entry `1aut`:
    >>> xref('pdb-1aut')

    This could be specially useful to retrieve all entries involved within a certain pathway,
    or another common cross-referenced database.

    For a list of supported databases, check `UniProtMapper.utils.read_fields_table()['returned_field']`.
    """

    def __init__(self, field_value: str) -> None:
        """Initialize the `xref` UniProtKB data field.

        Args:
            field_value: The cross-reference to search for.
        """
        super().__init__("xref", field_value)


class ec(SimpleField):
    """Query for entries with a certain EC number - specific for enzymes"""

    def __init__(self, field_value: str) -> None:
        """Initialize the `ec` UniProtKB data field.

        Args:
            field_value: The EC number to search for.
        """
        super().__init__("ec", field_value)


class existence(SimpleField):
    """Query for entries with a certain existence score. Possible values are:

    1. Experimental evidence at protein level
    2. Experimental evidence at transcript level
    3. Protein inferred from homology
    4. Protein predicted
    5. Protein uncertain

    For further information, check: https://www.uniprot.org/help/protein_existence
    """

    def __init__(self, field_value: str) -> None:
        """Initialize the `existence` UniProtKB data field.

        Args:
            field_value: The existence score to search for.
        """
        super().__init__("existence", field_value)


class family(SimpleField):
    """Query for entries within a certain protein family. Further functionalities include:
    - Query for "name_1" while excluding entries with "name_2" as family,
    >>> family('name_1 - name_2')
    - Query for "name_1" *and* "name_2", in this order,
    >>> family('name_1 name_2')
    - Glob-like search for all entries with family starting with "chemokine":
    >>> family('chemokine*')

    For a full list of protein families within UniProt, check:
    https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/docs/similar.txt
    """

    def __init__(self, field_value: str) -> None:
        """Initialize the `family` UniProtKB data field.

        Args:
            field_value: The protein family to search for.
        """
        super().__init__("family", field_value)


class gene(SimpleField):
    """Query for entries with a gene name. Caveat, searching for HPSE using this field
    will also retrieve entries with HPSE2. For a more specific search, use `GeneExact`.
    """

    def __init__(self, field_value: str) -> None:
        """Initialize the `gene` UniProtKB data field.

        Args:
            field_value: The gene name to search for.
        """
        super().__init__("gene", field_value)


class gene_exact(SimpleField):
    """Query for entries with an exact gene name match."""

    def __init__(self, field_value: str) -> None:
        """Initialize the `gene_exact` UniProtKB data field.

        Args:
            field_value: The exact gene name to search for.
        """
        super().__init__("gene_exact", field_value)


class go(SimpleField):
    """Query for entries with a certain Gene Ontology (GO) term. Further functionalities include:

    - Query for "name_1" while excluding entries with "name_2" as GO term,
    >>> go('name_1 - name_2')
    """

    def __init__(self, field_value: str) -> None:
        """Initialize the `go` UniProtKB data field.

        Args:
            field_value: The GO identifier to search for.
        """
        super().__init__("go", field_value)


class virus_host_name(SimpleField):
    """Search for all entries belonging to viruses that infect the query host organism.
    Input should be the name of the host organism. Both common and scientific names should work.

    For more information on the organism names, see: https://www.uniprot.org/taxonomy?query=*
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `virus_host_name` UniProtKB data field.

        Args:
            field_value: The host organism name to search for.
        """
        super().__init__("virus_host_name", field_value)


class virus_host_id(SimpleField):
    """Search for all entries belonging to viruses that infect the query host organism.
    Input should be the taxonomy ID of the host organism.

    For more information on the ID for your organism, see: https://www.uniprot.org/taxonomy?query=*
    """

    def __init__(self, field_value: Union[str, int]) -> None:
        """Initalize the `virus_host_id` UniProtKB data field.

        Args:
            field_value: The host organism taxonomy ID to search for.
        """
        super().__init__(
            "virus_host_id",
            (field_value if isinstance(field_value, str) else str(field_value)),
        )


class accession_id(SimpleField):
    """Query for entries with a certain accession ID."""

    def __init__(self, field_value: str) -> None:
        """Initalize the `accession_id` UniProtKB data field.

        Args:
            field_value: The accession ID to search for.
        """
        super().__init__("accession_id", field_value)


class inchikey(SimpleField):
    """Query entries associated with the small molecule identified by the input InChIKey

    For more information, check: https://www.uniprot.org/help/chemical_data_search
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `inchikey` UniProtKB data field.

        Args:
            field_value: The InChIKey to search for.
        """
        super().__init__("inchikey", field_value)


class interactor(SimpleField):
    """Input should be a UniProt accession key (ID). Query all entries describing
    interactions with the protein represented by the input."""

    def __init__(self, field_value: str) -> None:
        """Initalize the `interactor` UniProtKB data field.

        Args:
            field_value: The UniProt accession key to search for.
        """
        super().__init__("interactor", field_value)


class keyword(SimpleField):
    """Query all UniProt entries with a certain keyword. Further functionalities include:

    - Query for "name_1" while excluding entries with "name_2" as keyword,
    >>> keyword('name_1 - name_2')
    - Query for "name_1" *and* "name_2", in this order,
    >>> keyword('name_1 name_2')
    - Glob-like search for all entries with keyword starting with "G-protein":
    >>> keyword('G-protein*')

    For a list of keywords, check: https://www.uniprot.org/keywords?query=*
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `keyword` UniProtKB data field.

        Args:
            field_value: The keyword to search for.
        """
        super().__init__("keyword", field_value)


class cc_mass_spectrometry(SimpleField):
    """Check UniProt's official documentation for the description of this field:

    https://www.uniprot.org/help/query-fields#:~:text=least%20500%2C000%20Da.-,cc_mass_spectrometry,-cc_mass_spectrometry%3Amaldi
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `cc_mass_spectrometry` UniProtKB data field. For more information,
        check: https://www.uniprot.org/help/query-fields#:~:text=least%20500%2C000%20Da.-,cc_mass_spectrometry,-cc_mass_spectrometry%3Amaldi

        Args:
            field_value: The mass spectrometry information to search for.
        """
        super().__init__("cc_mass_spectrometry", field_value)


class organelle(SimpleField):
    """Query entries for proteins encoded by a gene within a certain organelle.

    E.g.: query entries encoded by the mitochondrial chromosome:
    >>> organelle('Mitochondrion')
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `organelle` UniProtKB data field.

        Args:
            field_value: The organelle to search for.
        """
        super().__init__("organelle", field_value)


class organism_id(SimpleField):
    """Query for entries with a certain organism taxonomy ID.

    For more information on the taxonomy IDs, see: https://www.uniprot.org/taxonomy?query=*
    """

    def __init__(self, field_value: Union[str, int]) -> None:
        """Initalize the `organism_id` UniProtKB data field.

        Args:
            field_value: The organism taxonomy ID to search for.
        """
        super().__init__(
            "organism_id",
            (field_value if isinstance(field_value, str) else str(field_value)),
        )


class plasmid(SimpleField):
    """Query entries for proteins encoded by a gene that is part of a certain plasmid.

    For the available plasmid vocabulary, check:
    https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/docs/plasmid.txt
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `plasmid` UniProtKB data field.

        Args:
            field_value: The plasmid to search for.
        """
        super().__init__("plasmid", field_value)


class proteome(SimpleField):
    """Query all proteins belonging to a certain proteome.

    For more information, check: https://www.uniprot.org/proteomes"""

    def __init__(self, field_value: str) -> None:
        """Initalize the `proteome` UniProtKB data field.

        Args:
            field_value: The proteome to search for.
        """
        super().__init__("proteome", field_value)


class proteome_component(SimpleField):
    """Query all proteins belonging to a certain proteome component.

    E.g.: Lists all entries from the human chromosome 1.
    >>> organism_id('9606') & proteome_component('chromosome:1')
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `proteome_component` UniProtKB data field.

        Args:
            field_value: The proteome component to search for.
        """
        super().__init__("proteomecomponent", field_value)


class sec_acc(SimpleField):
    """Query entries that were created from a merge with a certain UniProt entry.

    For more information, check UniProt's FAQ:
    https://www.uniprot.org/help/difference_accession_entryname"""

    def __init__(self, field_value: str) -> None:
        """Initalize the `sec_acc` UniProtKB data field.

        Args:
            field_value: The secondary accession key to search for.
        """
        super().__init__("sec_acc", field_value)


class scope(SimpleField):
    """Query entries containing a reference that was used to gather information about `<field_value>`.

    E.g.: for entries containing references with information about "mutagenesis", use:
    >>> scope('mutagenesis')
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `scope` UniProtKB data field.

        Args:
            field_value: The scope to search for. E.g. "mutagenesis" will search for all entries
                containing references with information about mutagenesis.
        """
        super().__init__("scope", field_value)


class taxonomy_name(SimpleField):
    """Query for entries with a certain organism taxonomy name.

    For more information on thetaxonomy names, see: https://www.uniprot.org/taxonomy?query=*

    E.g: to search for all mammal proteins:
    >>> taxonomy_name('mammal')
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `taxonomy_name` UniProtKB data field.

        Args:
            field_value: The organism taxonomy name to search for.
        """
        super().__init__("taxonomy_name", field_value)


class taxonomy_id(SimpleField):
    """Query for entries with a certain organism taxonomy ID.

    For more information on the taxonomy IDs, see: https://www.uniprot.org/taxonomy?query=*
    """

    def __init__(self, field_value: Union[str, int]) -> None:
        """Initalize the `taxonomy_id` UniProtKB data field.

        Args:
            field_value: The organism taxonomy ID to search for.
        """
        super().__init__(
            "taxonomy_id",
            (field_value if isinstance(field_value, str) else str(field_value)),
        )


class tissue(SimpleField):
    """Query entries containing a reference describing the protein sequence obtained
    from a clone isolated from a certain tissue. For a full list of UniProt's tissue
    vocabulary, check:

    https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/docs/tisslist.txt

    Further functionalities include:
    - Query for "name_1" while excluding entries with "name_2" as tissue,
    >>> tissue('name_1 - name_2')
    - Query for "name_1" *and* "name_2", in this order,
    >>> tissue('name_1 name_2')
    - Glob-like search for all entries with tissue starting with "brain":
    >>> tissue('brain*')
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `tissue` UniProtKB data field. For a full list of UniProt's tissue
        vocabulary, check: https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/docs/tisslist.txt

        Args:
            field_value: The tissue to search for.
        """
        super().__init__("tissue", field_value)


class cc_webresource(SimpleField):
    """Query all entries with a certain web resource.

    E.g.: all proteins described in Wikipedia:
    >>> cc_webresource('Wikipedia')
    """

    def __init__(self, field_value: str) -> None:
        """Initalize the `cc_webresource` UniProtKB data field.

        Args:
            field_value: The web resource to search for.
        """
        super().__init__("cc_webresource", field_value)
