# -*- coding: utf-8 -*-
"""A Python wrapper for the UniProt Mapping RESTful API."""

from .field_retriever_api import UniProtRetriever  # noqa: F401
from .id_mapping_api import UniProtIDMapper  # noqa: F401
from .interface import abc_UniProtAPI  # noqa: F401
from .swiss_parser import SwissProtParser  # noqa: F401
