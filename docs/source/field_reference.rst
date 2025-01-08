Return Fields Reference
=====================

UniProtMapper supports a wide range of return fields from UniProt. These fields are organized by their types and can be used to specify which data you want to retrieve.

.. csv-table:: Supported Return Fields
   :header: "Label", "Field", "Type", "Category"
   :widths: 30, 25, 15, 30
   :file: ../../src/UniProtMapper/resources/uniprot_return_fields.csv
   :encoding: utf-8

Field Categories
--------------

The return fields are organized into several categories:

1. Names & Taxonomy
   - Basic identification and taxonomic information
   - Gene names, organism details, etc.

2. Sequences
   - Sequence-related information
   - Length, mass, variants, etc.

3. Function
   - Functional annotations
   - Activity, pathways, binding sites, etc.

4. Structure
   - Structural information
   - 3D structure, secondary structure elements, etc.

5. Cross-references
   - Links to external databases
   - Organized by database type (e.g., genomic, proteomic, etc.)

Usage Example
-----------

To specify which fields to retrieve::

    from UniProtMapper import ProtMapper

    mapper = ProtMapper()
    
    # Get specific fields
    result, failed = mapper.get(
        ["P30542"], 
        fields=["accession", "gene_names", "organism_name"]
    )