Field-Based Querying Tutorial
=============================

This tutorial demonstrates how to use UniProtMapper's field-based querying functionality.

Basic Field Queries
-------------------

Here's a simple example using boolean fields::

    from UniProtMapper import ProtMapper
    from UniProtMapper.uniprotkb_fields import reviewed, organism_name
    
    mapper = ProtMapper()
    
    # Find reviewed human proteins
    query = reviewed(True) & organism_name("human")
    result, failed = mapper.query(query)

Complex Queries
---------------

You can combine multiple fields with boolean operators::

    from UniProtMapper.uniprotkb_fields import (
        length,
        mass,
        date_modified,
        gene_exact
    )
    
    # Find human proteins:
    # - modified since 2024
    # - between 200-300 amino acids
    # - mass < 50kDa
    query = (
        organism_name("human") &
        date_modified("2024-01-01", "*") &
        length(200, 300) &
        mass("*", 50000)
    )

Field Types
-----------

UniProtMapper supports several types of fields:

Boolean Fields
~~~~~~~~~~~~~~
::

    from UniProtMapper.uniprotkb_fields import reviewed, fragment, is_isoform
    
    # Get reviewed entries that are not fragments
    query = reviewed(True) & ~fragment(True)

Range Fields
~~~~~~~~~~~~
::

    from UniProtMapper.uniprotkb_fields import length, mass
    
    # Proteins between 200-300 amino acids
    query = length(200, 300)

Date Range Fields
~~~~~~~~~~~~~~~~~
::

    from UniProtMapper.uniprotkb_fields import date_created, date_modified
    
    # Entries created in 2023
    query = date_created("2023-01-01", "2023-12-31")

Text-Based Fields
~~~~~~~~~~~~~~~~~
::

    from UniProtMapper.uniprotkb_fields import gene_exact, keyword, family
    
    # Proteins in kinase family with ATP-binding
    query = family("Kinase*") & keyword("ATP-binding")
