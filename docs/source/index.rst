Welcome to UniProtMapper's documentation!
=====================================

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
------------

1. Map UniProt cross-referenced IDs to other identifiers & vice-versa
2. Programmatically retrieve supported return and cross-reference fields
3. Query UniProtKB entries using complex field-based queries

Quick Start
-----------

Installation::

    pip install uniprot-id-mapper

Basic usage::

    from UniProtMapper import ProtMapper
    
    mapper = ProtMapper()
    
    # Map IDs
    result, failed = mapper.get(
        ids=["P30542", "Q16678"], 
        from_db="UniProtKB_AC-ID", 
        to_db="Ensembl"
    )

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`