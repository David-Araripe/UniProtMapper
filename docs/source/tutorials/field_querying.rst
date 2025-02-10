Field-Based Querying Tutorial
=============================

This tutorial demonstrates how to use UniProtMapper's field-based querying functionality.

Basic Field Queries
-------------------

A simple example on querying UniProtKB through field search::

    from UniProtMapper import ProtKB
    from UniProtMapper.uniprotkb_fields import reviewed, organism_name
    
    protkb = ProtKB()
    
    # Find reviewed human proteins
    query = reviewed(True) & organism_name("human")
    result, failed = protkb.get(query)

.. note::

    Running this code will take some time as it retrieves all reviewed human proteins! Each iteration of the displayed progress bar represents 500 entries fetched from UniProtKB.

Complex Queries
---------------

You can combine multiple fields with boolean operators, illustrated by the following examples:

Example 1::

    from UniProtMapper import ProtKB
    from UniProtMapper.uniprotkb_fields import (
        organism_name,
        length,
        mass,
        date_modified,
    )

    protkb = ProtKB()
    
    # Find human proteins:
    # - NOT modified after 2023 (in UniProtKB)
    # - between 200-300 amino acids
    # - mass < 50kDa
    query = (
        organism_name("human") &
        length(200, 300) &
        mass("*", 50000) &
        (~ date_modified("2023-01-01", "*"))
    )
    result = protkb.get(query)

Example 2::

    from UniProtMapper import ProtKB
    from UniProtMapper.uniprotkb_fields import (
        xref_count,
        organism_id,
        reviewed,
        fragment,
        length,
    )

    protkb = ProtKB()

    # Find human proteins:
    # - with 2 or more deposited pdb strctures
    # - not fragments fragments
    # - reviewed
    # - length < 750 amino acids
    query = (
        xref_count("pdb", 2, "*")
        & organism_id(9606)
        & reviewed(True)
        & fragment(False)
        & length("*", 750)
    )
    result = protkb.get(query)

.. note::

    The ``fields`` parameter is also supported by the ``ProtKB`` API. For a full list of the supported fields, check the :ref:`supported_fields` section of the docs.

Field Types
-----------

UniProtMapper supports several types of fields. For full documentation on the fields implemented in the package, check :ref:`field_querying`. 

See below for examples of different field types implemented in UniProtMapper.

Boolean Fields
~~~~~~~~~~~~~~
::

    from UniProtMapper.uniprotkb_fields import reviewed, fragment, is_isoform
    
    # Example: Get reviewed entries that are not fragments
    query = reviewed(True) & ~fragment(True)

Range Fields
~~~~~~~~~~~~
::

    from UniProtMapper.uniprotkb_fields import length, mass
    
    # Example: Proteins between 200-300 amino acids
    query = length(200, 300)

Date Range Fields
~~~~~~~~~~~~~~~~~
::

    from UniProtMapper.uniprotkb_fields import date_created, date_modified
    
    # Example: Entries created in 2023
    query = date_created("2023-01-01", "2023-12-31")

Text-Based Fields
~~~~~~~~~~~~~~~~~
::

    from UniProtMapper.uniprotkb_fields import gene_exact, keyword, family
    
    # Example: Proteins in kinase family with ATP-binding
    query = family("Kinase*") & keyword("ATP-binding")
