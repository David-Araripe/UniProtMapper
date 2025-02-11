Return Fields Reference
=======================

UniProtMapper supports a wide range of return fields from UniProt. These fields are organized by their types and can be used to specify data you want to get for the proteins retrieved by your query.

UniProt return fields are organized into the categories:

1. **Names & Taxonomy**: Basic identification and taxonomic information. *E.g.:*: Gene names, organism details, etc.

2. **Sequences**: Sequence-related information. *E.g.:*: Length, mass, variants, etc.

3. **Function**: Functional annotations. *E.g.:*: Activity, pathways, binding sites, etc.

4. **Structure**: Structural information. *E.g.:*: 3D structure, secondary structure elements, etc.

5. **Cross-references**: Links to external databases, subdivided into different categories according to the database being cross-referenced. *E.g.:* `Chemistry` for datasets like `DrugBank`, `Genome annotation` for `Ensembl`, etc.

.. _supported_fields:
Supported fields
----------------

The supported return fields are listed below. The columns contain different information about the fields:

- **label**: The label used by UniProt to represent this field. Also used as column names on the `pd.DataFrame` returned from `get` methods implemented on both APIs.
- **returned_field**: Name used to specify which information to retrieve by the APIs. For examples, check below.
- **field_type**: The category of the field, as listed above under `Field Categories`. Note that for `type=='cross_reference'`, the field_type is the category of the cross-referenced database.
- **has_full_version**: Not available for `type=='uniprot_field'`. If `yes`, a "full" version of the return field is accessible by using ``<field_name>_full``.
- **type**: Either "uniprot_field" or "cross_reference". The former indicates a field that is directly related to the protein, while the latter indicates a field that is a cross-reference to another database and not native to UniProt.

For more up-to-date information on `has_full_version` of cross-referenced fields, check the official UniProt documentation: `Return Fields <https://www.uniprot.org/help/return_fields_databases>`_. In case of discrepancies, issues or pull requests are welcome!

.. csv-table:: Supported Return Fields
   :header-rows: 1
   :file: _static/uniprot_return_fields.csv

Specify Return Fields with ID Mapping API
-----------------------------------------

Specify which fields to retrieve on a ID mapping request::

    from UniProtMapper import ProtMapper

    mapper = ProtMapper()
    
    fields = ["accession", "gene_names", "organism_name"]
    result, failed = mapper.get(
        ["P30542"], 
        fields=fields,
    )

Specify Return Fields with UniProtKB API
----------------------------------------

Specify which fields to retrieve on a field-based query::
   
   from UniProtMapper import ProtKB
   from UniProtMapper.uniprotkb_fields import accession

   protkb = ProtKB()

   query = accession("P30542")
   fields = ["accession", "gene_names", "organism_name"]
   result, failed = protkb.get(
        query,
        fields=fields,
   )
