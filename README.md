[![Linting Ruff](https://img.shields.io/badge/Linting%20-Ruff-red?style=flat-square)](https://github.com/charliermarsh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black?style=flat-square)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat-square&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2FDavid-Araripe%2FUniProtMapper%2Fbadge%3Fref%3Dmaster&style=flat-square)](https://actions-badge.atrox.dev/David-Araripe/UniProtMapper/goto?ref=master)
[![Downloads:PyPI](https://img.shields.io/pypi/dm/uniprot-id-mapper?style=flat-square)](https://pypi.org/project/uniprot-id-mapper/)

# UniProtMapper

A (unofficial) Python wrapper for the [UniProt Retrieve/ID Mapping](https://www.uniprot.org/id-mapping) RESTful API. This package supports the following functionalities:

- Map UniProt IDs other identifiers (handled by [UniProtIDMapper](#uniprotidmapper));
- Retrieve any of the supported [return fields](https://www.uniprot.org/help/return_fields) (handled by [UniprotRetriever](#uniprotretriever))
- Parse json UniProt-SwissProt responses (handled by [SwissProtParser](#swissprotparser)).

## Installation

From PyPI:
``` Shell
pip install uniprot-id-mapper
```

From source:
``` Shell
git clone https://github.com/David-Araripe/UniProtMapper
cd UniProtMapper
pip install .
```
## Usage

<summary>

## UniProtIDMapper

</summary>
<details>

Supported databases and their respective type are stored under the attribute `self.supported_dbs_with_types`. These are also found as a list under `self._supported_fields`.
``` Python
from UniProtMapper import UniProtIDMapper

mapper = UniProtIDMapper()
print(mapper.supported_dbs_with_types)
```

To map a list of UniProt IDs to Ensembl IDs, the user can either call the object directly or use the `mapID` method.
``` Python
result, failed = mapper.mapIDs(
    ids=["P30542", "Q16678", "Q02880"], from_db="UniProtKB_AC-ID", to_db="Ensembl"
)
>>> Retrying in 3s
>>> Fetched: 3 / 3

result, failed = mapper(
    ids=["P30542", "Q16678", "Q02880"], from_db="UniProtKB_AC-ID", to_db="Ensembl"
)
>>> Retrying in 3s
>>> Fetched: 3 / 3
```

Where result is the following pandas DataFrame:

|    | UniProtKB_AC-ID   | Ensembl            |
|---:|:------------------|:-------------------|
|  0 | P30542            | ENSG00000163485.17 |
|  1 | Q16678            | ENSG00000138061.12 |
|  2 | Q02880            | ENSG00000077097.17 |

</details>
<summary>

## UniProtRetriever

</summary>
<details>

This class supports retrieving any of the UniProt [return fields](https://www.uniprot.org/help/return_fields). The user can access these directly from the object, under the attribute `self.fields_table`, e.g.:

```Python
from UniProtMapper import UniProtRetriever

field_retriever = UniProtRetriever()
df = field_retriever.fields_table
df.head()
```
|    | Label                | Legacy Returned Field   | Returned Field   | Field Type       |
|---:|:---------------------|:------------------------|:-----------------|:-----------------|
|  0 | Entry                | id                      | accession        | Names & Taxonomy |
|  1 | Entry Name           | entry name              | id               | Names & Taxonomy |
|  2 | Gene Names           | genes                   | gene_names       | Names & Taxonomy |
|  3 | Gene Names (primary) | genes(PREFERRED)        | gene_primary     | Names & Taxonomy |
|  4 | Gene Names (synonym) | genes(ALTERNATIVE)      | gene_synonym     | Names & Taxonomy |

Similar to `UniProtIDMapper`, the user can either call the object directly or use the `retrieveFields` method to obtain the response.

```Python
result, failed = field_retriever.retrieveFields(["Q02880"])
>>> Fetched: 1 / 1

result, failed = field_retriever(["Q02880"])
>>> Fetched: 1 / 1
```

Custom returned fields can be retrieved by passing a list of fields to the `fields` parameter. These fields need to be within `UniProtRetriever.fields_table["Returned Field"]` and will be returned with columns named as their respective `Label`.

The object already has a list of default fields under `self.default_fields`, but these are ignored if the parameter `fields` is passed.

```Python
fields = ["accession", "organism_name", "structure_3d"]
result, failed = field_retriever.retrieveFields(["Q02880"],
                                                fields=fields)
```
</details>
<summary>

## SwissProtParser

</summary>
<details>

### Querying data from UniProt-SwissProt

Retrieving json UniProt-SwissProt (reviewed) responses is also possible, such as the following:

``` Python
result, failed = mapper(
    ids=["P30542", "Q16678", "Q02880"], from_db="UniProtKB_AC-ID", to_db="UniProtKB-Swiss-Prot"
)

print(result.loc[0, 'to'])
>>> {'from': 'P30542',
>>>  'to': {'entryType': 'UniProtKB reviewed (Swiss-Prot)',
>>>   'primaryAccession': 'P30542',
>>> ...
>>>     'Beta strand': 2,
>>>     'Turn': 1},
>>>    'uniParcId': 'UPI00000503E1'}}}
```

SwissProt responses from `UniProtIDMapper` can be parsed using the `SwissProtParser` class, where the fields to extract from UniProt (:param: = toquery) are stored under `self._supported_fields` and the cross-referenced datasets are stored under `self._crossref_dbs` (:param: = crossrefs).

``` Python
from UniProtMapper import SwissProtParser

parser = SwissProtParser(
    toquery=["organism", "tissueExpression", "cellLocation"], crossrefs=["GO"]
)
parser(result.loc[0, 'to'])

>>> {'organism': 'Homo sapiens',
>>>  'tissueExpression': '',
>>>  'cellLocation': 'Cell membrane',
>>>  'GO_crossref': ['GO:0030673~GoTerm~C:axolemma',
>>>   'GO:0030673~GoEvidenceType~IEA:Ensembl',
>>> ...
>>>   'GO:0007165~GoEvidenceType~TAS:ProtInc',
>>>   'GO:0001659~GoTerm~P:temperature homeostasis',
>>>   'GO:0001659~GoEvidenceType~IEA:Ensembl',
>>>   'GO:0070328~GoTerm~P:triglyceride homeostasis',
>>>   'GO:0070328~GoEvidenceType~IEA:Ensembl']}
```

Both `UniProtIDMapper.mapIDs` and `__call__` methods accept a `SwissProtParser` as a parameter, such as in:

``` Python
result, failed = mapper(
    ids=["P30542", "Q16678", "Q02880"],
    from_db="UniProtKB_AC-ID",
    to_db="UniProtKB-Swiss-Prot",
    parser=parser,
)
```
</details>

<summary>

## Mapping identifiers to orthologs

</summary>
<details>

This package also allows mapping UniProt IDs to orthologs. The function `uniprot_ids_to_orthologs` does that by mapping UniProt IDs to OrthoDB and then re-mapping these results to UniProt-SwissProt. Desired fields to retrieve using `SwissProtParser` can be specified with the parameters `uniprot_info` and `crossref_dbs`.

Queried objects are in the column `original_id` and their OrthoDB identifier is found on `orthodb_id`.
``` Python
from UniProtMapper import UniProtIDMapper

mapper = UniProtIDMapper()
result, failed = mapper.uniprotIDsToOrthologs(
    ids=["P30542", "Q16678", "Q02880"], organism="Mus musculus"
)

# Fetched results contain all retrieved species.
# Filtering by organism is done on the full response.
>>> Fetched: 3 / 3
>>> Fetched: 246 / 246
```

Alternatively, OrthoDB IDs can be obtained using UniProtIDMapper, and used to retrieve any of the desired UniProt return fields using UniProtRetriever.

``` Python
from UniProtMapper import UniProtIDMapper, UniProtRetriever

mapper = UniProtIDMapper()
result, failed = mapper(
    ids=["P30542", "Q16678", "Q02880"],
    from_db="UniProtKB_AC-ID",
    to_db="OrthoDB",
)
field_retriever = UniProtRetriever()
ortho_results, failed = field_retriever.retrieveFields(
    ids=result["to"].tolist(), from_db="OrthoDB"
)

>>> Retrying in 3s
>>> Fetched: 3 / 3
>>> Retrying in 3s
>>> Fetched: 246 / 246
```
</details>