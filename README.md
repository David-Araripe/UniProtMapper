[![Linting Ruff](https://img.shields.io/badge/Linting%20-Ruff-red?style=flat-square)](https://github.com/charliermarsh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black?style=flat-square)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat-square&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](https://opensource.org/licenses/MIT)

# UniProtMapping

A Python wrapper for the [UniProt Mapping](https://www.uniprot.org/id-mapping) RESTful API.

➡️ Map UniProt IDs other identifiers and parse UniProt-SwissProt responses.

## Installation

> yet to make the package available on PyPI...


## Usage

Supported databases for mapping are saved under `supported_dbs_with_types`.
``` Python
from UniProtMapper import UniProtMapper

mapper = UniProtMapper()
print(mapper.supported_dbs_with_types)
```

To map a list of UniProt IDs to Ensembl IDs, either the user can either call the object directly or use the `uniprot_id_mapping` method.
``` Python
result, failed = mapper.uniprot_id_mapping(
    ids=["P30542", "Q16678", "Q02880"], from_db="UniProtKB_AC-ID", to_db="Ensembl"
)
>>> Retrying in 3s
>>> Fetched: 3 / 3

result, failed = mapper(
    ids=["P30542", "Q16678", "Q02880"], from_db="UniProtKB_AC-ID", to_db="Ensembl"
)
>>> Retrying in 3s
>>> Fetched: 3 / 3

# Where the results are organized as a nested dictionary:
print(result[0])
>>> {'from': 'P30542', 'to': 'ENSG00000163485.17'}
```

Retrieved results are easily converted to a pandas DataFrame.
``` Python
import pandas as pd

df = pd.DataFrame.from_dict(result, orient="index").rename(
    columns={"from": "UniProtKB_AC-ID", "to": "Ensembl"}
)
```
With the resulting DataFrame being:

|    | UniProtKB_AC-ID   | Ensembl            |
|---:|:------------------|:-------------------|
|  0 | P30542            | ENSG00000163485.17 |
|  1 | Q16678            | ENSG00000138061.12 |
|  2 | Q02880            | ENSG00000077097.17 |

### Querying data from UniProt-SwissProt

Retrieving UniProt-SwissProt (reviewed) is also possible, but the retrieved response is much more complex:

``` Python
result, failed = mapper(
    ids=["P30542", "Q16678", "Q02880"], from_db="UniProtKB_AC-ID", to_db="UniProtKB-Swiss-Prot"
)

print(result[0])
>>> {'from': 'P30542',
>>>  'to': {'entryType': 'UniProtKB reviewed (Swiss-Prot)',
>>>   'primaryAccession': 'P30542',
>>> ...
>>>     'Beta strand': 2,
>>>     'Turn': 1},
>>>    'uniParcId': 'UPI00000503E1'}}}
```
### Parsing UniProt-SwissProt responses

SwissProt responses can be parsed using the `SwissProtParser` class, where the supported fields to be extracted from UniProt (param=toquery) are stored under `self._supported_fields` and the cross-referenced datasets are stored under `self._crossref_dbs` (param=crossrefs).


``` Python
parser = SwissProtParser(
    toquery=["organism", "tissueExpression", "cellLocation"], crossrefs=["GO"]
)
parser(result[0]['to'])

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

### Mapping identifiers to orthologs

This package also allows mapping UniProt IDs to orthologs. The function `uniprot_ids_to_orthologs` does that by mapping UniProt IDs to OrthoDB and then re-mapping these results to UniProt-SwissProt.

The user can also specify which information fields to retrieve with the parameters `uniprot_info` and `crossref_dbs`. Leaving those as default will retrieve all supported UniProt information and no cross-references.

Queried objects are in the column `original_id` and their OrthoDB identifier is found on `orthodb_id`.
``` Python
mapper = UniProtMapper()
result, failed = mapper.uniprot_ids_to_orthologs(
    ids=["P30542", "Q16678", "Q02880"], organism="Mus musculus"
)

# Fetched results contain all retrieved species.
# Filtering by organism is done on the full response.
>>> Fetched: 3 / 3
>>> Fetched: 349 / 349
```