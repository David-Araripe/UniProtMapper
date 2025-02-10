ID Mapping Tutorial
===================

This tutorial demonstrates how to use UniProtMapper to map between different types of identifiers.

Basic Mapping
-------------

Here's a simple example of mapping UniProt accession IDs to Ensembl IDs::

    from UniProtMapper import ProtMapper
    
    mapper = ProtMapper()
    
    result, failed = mapper.get(
        ids=["P30542", "Q16678", "Q02880"],
        from_db="UniProtKB_AC-ID",
        to_db="Ensembl"
    )

The ``result`` is a `pandas.DataFrame` containing the query and mapped IDs (column names `From` and `To`, respectively), while ``failed`` is a list of IDs that couldn't be mapped.

Mapping Through Cross-Referenced Fields
---------------------------------------

Ensembl is also cross-referenced in UniProt entries. In case you're interested in checking all cross-referenced Ensembl IDs for a given UniProt entry, you can do so by::

    from UniProtMapper import ProtMapper
    
    mapper = ProtMapper()
    
    fields = ["xref_ensembl"]
    result, failed = mapper.get(
        ids=["P30542", "Q16678", "Q02880"],
        fields=fields,
    )

.. note::

    For a full list of the supported fields, check the :ref:`supported_fields` section of the docs. Here, result is again a `pandas.DataFrame` containing the query and mapped IDs (column names `From` and `Ensembl`, following the `label` column in the reference table).

Available Databases
-------------------

UniProtMapper supports mapping between numerous databases. You can view the complete list of supported databases in ``ProtMapper()._supported_dbs`` or check UniProt's documentation.

Handling Failed Mappings
------------------------

Some IDs might fail to map if the identifier you're working with is not listed on the cross-references of a certain UniProt entry. Therefore, `ProtMapper.get` method will always return two values, with the first being the result and the second, a list of IDs that failed to be mapped (an empty list if all IDs were successfully mapped). Here's how to handle failed mappings::

    # Check if there were any failed mappings
    if failed:
        print(f"Failed to map {len(failed)} IDs:")
        print(f"- {' '.join(id)}")

Batch Processing
----------------

For large sets of IDs, UniProtMapper automatically handles batch processing::

    # Large list of IDs
    ids = ["P30542", "Q16678", ..., "Q02880"]
    
    # UniProtMapper will handle batching automatically
    result, failed = mapper.get(
        ids=ids,
        from_db="UniProtKB_AC-ID",
        to_db="Ensembl"
    )
