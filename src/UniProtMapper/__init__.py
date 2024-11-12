"""A Python wrapper for the UniProt id-mapping RESTful API: https://www.uniprot.org/id-mapping"""

try:
    from .idmapping_api import ProtMapper  # noqa: F401
    from .uniprotkb_api import ProtKB  # noqa: F401
except ImportError:  # when installing the package with setuptools_scm
    pass

from .version_helper import get_version

__version__ = get_version()
