Welcome to UniProtMapper's documentation!
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   field_reference
   api/modules
   tutorials/mapping
   tutorials/retrieving
   tutorials/field_querying

UniProtMapper is a Python wrapper for UniProt's Retrieve/ID Mapping RESTful API.

Main Features
-------------

1. Map UniProt cross-referenced IDs to other identifiers & vice-versa
2. Programmatically retrieve supported return and cross-reference fields (see :ref:`supported_fields`)
3. Query UniProtKB entries using complex field-based queries (see :ref:`field_querying`)

Quick Start
-----------

Installation::

    pip install uniprot-id-mapper

**Example 1**. Use UniProtMapper to easily map between different protein identifiers::

    from UniProtMapper import ProtMapper

    mapper = ProtMapper()

    result, failed = mapper.get(
        ids=["P30542", "Q16678", "Q02880"], from_db="UniProtKB_AC-ID", to_db="Ensembl"
    )

**Example 2**. Programmatically retrieve fields from UniProtKB entries::

    from UniProtMapper import ProtMapper

    mapper = ProtMapper()

    fields = ["accession", "gene_names", "organism_name"]
    result, failed = mapper.get(
        ids=["P30542", "Q16678", "Q02880"], fields=fields
    )

**Example 3**. Query UniProtKB entries using complex field-based queries::

    from UniProtMapper import ProtKB
    from UniProtMapper.uniprotkb_fields import (
        organism_name, 
        length, 
        reviewed, 
        date_modified
    )

    # Find reviewed human proteins with length between 100-200 amino acids
    # that were modified after January 1st, 2024
    query = (
        organism_name("human") & 
        reviewed(True) & 
        length(100, 200) & 
        date_modified("2024-01-01", "*")
    )

    protkb = ProtKB()
    result = protkb.get(query)


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`