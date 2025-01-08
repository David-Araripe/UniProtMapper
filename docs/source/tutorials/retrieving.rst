Retrieving Information Tutorial
===============================

This tutorial shows how to retrieve information about proteins from UniProt.

Basic Retrieval
---------------

Here's how to retrieve information about a protein::

    from UniProtMapper import ProtMapper
    
    mapper = ProtMapper()
    
    # Get information using default fields
    result, failed = mapper.get(["Q02880"])

Customizing Return Fields
-------------------------

You can specify which fields to retrieve::

    # List available fields
    fields_df = mapper.fields_table
    print(fields_df.head())
    
    # Get specific fields
    fields = ["accession", "organism_name", "structure_3d"]
    result, failed = mapper.get(["Q02880"], fields=fields)

Default Fields
--------------

UniProtMapper comes with a set of default fields, but you can override them::

    # Check default fields
    print(mapper.default_fields)
    
    # Use custom fields instead
    result, failed = mapper.get(
        ["Q02880"],
        fields=["accession", "gene_names", "length"]
    )

Handling Multiple Entries
-------------------------

You can retrieve information for multiple proteins at once::

    ids = ["P30542", "Q16678", "Q02880"]
    result, failed = mapper.get(ids)

The results will be returned as a pandas DataFrame with one row per protein.
