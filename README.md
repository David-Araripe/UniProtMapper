[![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black?style=flat-square)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat-square&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![GitHub Actions](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2FDavid-Araripe%2FUniProtMapper%2Fbadge%3Fref%3Dmaster&style=flat-square)](https://actions-badge.atrox.dev/David-Araripe/UniProtMapper/goto?ref=master)
[![Downloads:PyPI](https://img.shields.io/pypi/dm/uniprot-id-mapper?style=flat-square)](https://pypi.org/project/uniprot-id-mapper/)

# UniProtMapper <img align="left" width="40" height="40" src="https://raw.githubusercontent.com/whitead/protein-emoji/main/src/protein-72-color.svg">

Easily retrieve UniProt data and map protein identifiers using this Python package for UniProt's Retrieve & ID Mapping RESTful APIs. [Read the full documentation](https://david-araripe.github.io/UniProtMapper/stable/index.html).

## 📚 Table of Contents

- [⛏️ Features](#️-features)
- [📦 Installation](#-installation)
- [🛠️ Usage](#️-usage)
  - [Mapping IDs](#mapping-ids)
  - [Retrieving Information](#retrieving-information)
  - [Field-based Querying](#field-based-querying)
- [📖 Documentation](#-documentation)
- [💻 Command Line Interface (CLI)](#-command-line-interface-cli)
- [👏🏼 Credits](#-credits)

## ⛏️ Features
UniProtMapper is a tool for bioinformatics and proteomics research that supports:

1. Mapping any UniProt [cross-referenced IDs](https://github.com/David-Araripe/UniProtMapper/blob/master/src/UniProtMapper/resources/uniprot_mapping_dbs.json) to other identifiers & vice-versa;
2. Programmatically retrieving any of the supported [return](https://www.uniprot.org/help/return_fields) and [cross-reference fields](https://www.uniprot.org/help/return_fields_databases) from both UniProt-SwissProt and UniProt-TrEMBL (unreviewed) databases. For a full table containing all the supported resources, refer to the [supported fields](https://david-araripe.github.io/UniProtMapper/stable/field_reference.html#supported-fields) in the docs;
3. Querying UniProtKB entries using complex field-based queries with boolean operators `~` (NOT), `|` (OR), `&` (AND).

For the first two functionalities, check the examples [Mapping IDs](#mapping-ids) and [Retrieving Information](#retrieving-information) below. The third, see [Field-based Querying](#field-based-querying). 

The ID mapping API can also be accessed through the CLI. For more information, check [CLI](#-command-line-interface-cli).

## 📦 Installation

### From PyPI (recommended):
```shell
python -m pip install uniprot-id-mapper
```

### Directly from GitHub:
```shell
python -m pip install git+https://github.com/David-Araripe/UniProtMapper.git
```

### From source:
```shell
git clone https://github.com/David-Araripe/UniProtMapper
cd UniProtMapper
python -m pip install .
```

# 🛠️ Usage

## Mapping IDs
Use UniProtMapper to easily map between different protein identifiers:

``` python
from UniProtMapper import ProtMapper

mapper = ProtMapper()

result, failed = mapper.get(
    ids=["P30542", "Q16678", "Q02880"], from_db="UniProtKB_AC-ID", to_db="Ensembl"
)
```
The `result` is a pandas DataFrame containing the mapped IDs (see below), while `failed` is a list of identifiers that couldn't be mapped.

|    | UniProtKB_AC-ID   | Ensembl            |
|---:|:------------------|:-------------------|
|  0 | P30542            | ENSG00000163485.17 |
|  1 | Q16678            | ENSG00000138061.12 |
|  2 | Q02880            | ENSG00000077097.17 |

## Retrieving Information

All [supported return fields](https://david-araripe.github.io/UniProtMapper/stable/field_reference.html#supported-fields) are both accessible through the attribute `ProtMapper.fields_table`:

```Python
from UniProtMapper import ProtMapper

mapper = ProtMapper()
df = mapper.fields_table
df.head()
```
|    | label                | returned_field   | field_type       | has_full_version   | type          |
|---:|:---------------------|:-----------------|:-----------------|:-------------------|:--------------|
|  0 | Entry                | accession        | Names & Taxonomy | -                  | uniprot_field |
|  1 | Entry Name           | id               | Names & Taxonomy | -                  | uniprot_field |
|  2 | Gene Names           | gene_names       | Names & Taxonomy | -                  | uniprot_field |
|  3 | Gene Names (primary) | gene_primary     | Names & Taxonomy | -                  | uniprot_field |
|  4 | Gene Names (synonym) | gene_synonym     | Names & Taxonomy | -                  | uniprot_field |

From the DataFrame, all `return_field` entries can be used to access UniProt data programmatically:

```Python
# To retrieve the default fields:
result, failed = mapper.get(["Q02880"])
>>> Fetched: 1 / 1

# Retrieve custom fields:
fields = ["accession", "organism_name", "structure_3d"]
result, failed = mapper.get(["Q02880"], fields=fields)
>>> Fetched: 1 / 1
```

## Field-based Querying

UniProtMapper supports complex field-based protein queries using boolean operators (AND, OR, NOT) through the `uniprotkb_fields` module. This allows you to create sophisticated searches combining multiple criteria. For example:

```python
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
```
For a list of all fields and their descriptions, check the API reference for the [uniprotkb_fields](https://david-araripe.github.io/UniProtMapper/stable/api/UniProtMapper.html#module-UniProtMapper.uniprotkb_fields) module reference.

## 📖 Documentation

- [Stable Branch Documentation](https://david-araripe.github.io/UniProtMapper/stable/index.html) (master branch)
- [Development  Documentation](https://david-araripe.github.io/UniProtMapper/dev/index.html) (dev branch)

# 💻 Command Line Interface (CLI)

UniProtMapper provides a CLI for the ID Mapping class, `ProtMapper`, for easy access to lookups and data retrieval. Here is a list of the available arguments, shown by `protmap -h`:

```text
usage: UniProtMapper [-h] -i [IDS ...] [-r [RETURN_FIELDS ...]] [--default-fields] [-o OUTPUT]
                     [-from FROM_DB] [-to TO_DB] [-over] [-pf]

Retrieve data from UniProt using UniProt's RESTful API. For a list of all available fields, see: https://www.uniprot.org/help/return_fields 

Alternatively, use the --print-fields argument to print the available fields and exit the program.

optional arguments:
  -h, --help            show this help message and exit
  -i [IDS ...], --ids [IDS ...]
                        List of UniProt IDs to retrieve information from. Values must be
                        separated by spaces.
  -r [RETURN_FIELDS ...], --return-fields [RETURN_FIELDS ...]
                        If not defined, will pass `None`, returning all available fields.
                        Else, values should be fields to be returned separated by spaces. See
                        --print-fields for available options.
  --default-fields, -def
                        This option will override the --return-fields option. Returns only the
                        default fields stored in: <pkg_path>/resources/cli_return_fields.txt
  -o OUTPUT, --output OUTPUT
                        Path to the output file to write the returned fields. If not provided,
                        will write to stdout.
  -from FROM_DB, --from-db FROM_DB
                        The database from which the IDs are. For the available cross
                        references, see: <pkg_path>/resources/uniprot_mapping_dbs.json
  -to TO_DB, --to-db TO_DB
                        The database to which the IDs will be mapped. For the available cross
                        references, see: <pkg_path>/resources/uniprot_mapping_dbs.json
  -over, --overwrite    If desired to overwrite an existing file when using -o/--output
  -pf, --print-fields   Prints the available return fields and exits the program.
```

Usage example, retrieving default fields from `<pkg_path>/resources/cli_return_fields.txt`:
<p align="center">
    <img src="https://github.com/David-Araripe/UniProtMapper/blob/master/figures/cli_example_fig.png?raw=true" alt="Image displaying the output of UniProtMapper's CLI, protmap"/>
</p>

## 👏🏼 Credits

- [UniProt](https://www.uniprot.org/) for providing the API and the amazing database;
- [Andrew White and the University of Rochester](https://github.com/whitead/protein-emoji) for the protein emoji;

---

For issues, feature requests, or questions, please open an issue on the GitHub repository.