"""Contain base classes for the different types of fields in UniProtKB

Used to create the fields within UniProtMapper.uniprot_kb_fields
"""

import re
from typing import Union

from .utils import read_fields_table

XREF_FIELDS = (
    read_fields_table()
    .query("returned_field.str.match('xref_')")["returned_field"]
    .str.replace("xref_", "")
    .to_list()
)


class QueryBuilder:
    """
    Query builder for UniProt KB queries using Python operators.

    Supports boolean operations through Python operators:
    - & : AND operation
    - | : OR operation
    - ~ : NOT operation

    Example:

        >>> reviewed = QueryBuilder([BooleanField("reviewed", True)])
        >>> human = QueryBuilder([SimpleField("organism_id", "9606")])
        >>> query = reviewed & human
        >>> str(query)
        'reviewed:true AND organism_id:9606'

        >>> complex_query = ~reviewed | (human & QueryBuilder([RangeField("length", "100", "200")]))
        >>> str(complex_query)
        'NOT reviewed:true OR (organism_id:9606 AND length:[100 TO 200])'
    """

    def __init__(self, query: Union[list[Union[str, "AnyField"]], "AnyField"]) -> None:
        """Initialize QueryBuilder with a query."""
        # Convert single field to list for consistency
        self.query = [query] if hasattr(query, "field_name") else query

        # Track operation type for precedence handling
        self.operation = None  # Can be 'AND', 'OR', or 'NOT'
        self.grouped = False

        # Validate query elements
        for q in self.query:
            if not (isinstance(q, str) or hasattr(q, "field_name")):
                raise ValueError(
                    f"Query elements must be strings or Field objects, got {type(q)}"
                )

    def __call__(self) -> "QueryBuilder":
        """Handle explicit parentheses grouping."""
        self.grouped = True
        return self

    def _combine(self, other: "QueryBuilder", operation: str) -> "QueryBuilder":
        """Helper method for combining queries with operators."""
        if not isinstance(other, QueryBuilder):
            raise TypeError(
                f"Can only combine QueryBuilder instances, got {type(other)}"
            )

        result = QueryBuilder([])
        result.operation = operation

        # Handle left operand
        if self.operation == operation and not self.grouped:
            result.query.extend(self.query)
        else:
            left_needs_parens = self.operation is not None and not self.grouped
            if left_needs_parens:
                result.query.extend(["("] + self.query + [")"])
            else:
                result.query.extend(self.query)

        # Add operator
        result.query.append(operation)

        # Handle right operand
        if other.operation == operation and not other.grouped:
            result.query.extend(other.query)
        else:
            right_needs_parens = other.operation is not None and not other.grouped
            if right_needs_parens:
                result.query.extend(["("] + other.query + [")"])
            else:
                result.query.extend(other.query)

        return result

    def __and__(self, other: "QueryBuilder") -> "QueryBuilder":
        """Combine queries with AND operator."""
        return self._combine(other, "AND")

    def __or__(self, other: "QueryBuilder") -> "QueryBuilder":
        """Combine queries with OR operator."""
        return self._combine(other, "OR")

    def __invert__(self) -> "QueryBuilder":
        """Negate the query with NOT operator."""
        result = QueryBuilder([])
        result.operation = "NOT"

        # Add NOT operator
        result.query.append("NOT")

        # Add parentheses if needed
        if self.operation is not None and not self.grouped:
            result.query.extend(["("] + self.query + [")"])
        else:
            result.query.extend(self.query)

        return result

    def __str__(self) -> str:
        """Convert query to string representation."""
        parts = []
        for i, element in enumerate(self.query):
            curr_str = str(element)

            # Special cases for no spaces
            if curr_str in ["(", ")"]:
                parts.append(curr_str)
                continue

            if curr_str == "NOT":
                if i > 0 and parts[-1] != "(":
                    parts.append(" ")
                parts.append(curr_str)
                continue

            # Add space before if needed
            if i > 0 and parts[-1] not in ["("]:
                parts.append(" ")

            parts.append(curr_str)

        return "".join(parts)

    def __repr__(self) -> str:
        return self.__str__()


class BooleanField:
    """Field for boolean values."""

    def __init__(self, field_name: str, field_value: bool):
        self.field_name = field_name
        self.field_value = self._bool_to_string(field_value)

    def _bool_to_string(self, value):
        if isinstance(value, bool):
            return str(value).lower()

    def __str__(self):
        return f"{self.field_name}:{self.field_value}"

    def __new__(cls, *args, **kwargs):
        """Create the field and return it wrapped in a QueryBuilder."""
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return QueryBuilder([instance])


class SimpleField:
    """Simple field query. Used for fields like accession, protein_name, etc"""

    def __init__(self, field_name: str, field_value: str) -> None:
        self.field_name = field_name
        self.field_value = field_value

    def __str__(self):
        return f"{self.field_name}:{self.field_value}"

    def __new__(cls, *args, **kwargs):
        """Create the field and return it wrapped in a QueryBuilder."""
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return QueryBuilder([instance])


class QuoteField:
    """Same as SimpleField but it quotes the value. Used for species, for example"""

    def __init__(self, field_name: str, field_value: str) -> None:
        self.field_name = field_name
        self.field_value = field_value

    def __str__(self):
        return f"{self.field_name}:'{self.field_value}'"

    def __new__(cls, *args, **kwargs):
        """Create the field and return it wrapped in a QueryBuilder."""
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return QueryBuilder([instance])


class DateRangeField:
    """Field for date ranges. If desired, the date can be set to '*' to fetch until most recent."""

    def __init__(self, field_name: str, from_date: str, to_date) -> None:
        self.field_name = field_name
        self.from_date = self._format_checker(from_date, date_type="Initial")
        self.to_date = self._format_checker(to_date, date_type="Final")

    def _format_checker(self, date: str, date_type: str) -> str:
        if not re.match(r"\d{4}-\d{2}-\d{2}", date) and date != "*":
            raise ValueError(
                f"{date_type} in the incorrect format. Make sure to have it as YYYY-MM-DD"
            )
        return date

    def __str__(self):
        return f"{self.field_name}:[{self.from_date} TO {self.to_date}]"

    def __new__(cls, *args, **kwargs):
        """Create the field and return it wrapped in a QueryBuilder."""
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return QueryBuilder([instance])


class RangeField:
    """Field for ranges. If desired, numbers can be set to * to fetch until 0 or infinity"""

    def __init__(
        self, field_name: str, from_value: Union[str, int], to_value: Union[str, int]
    ) -> None:
        self.field_name = field_name
        self.from_value = self._format_checker(from_value, value_type="Initial")
        self.to_value = self._format_checker(to_value, value_type="Final")

    def _format_checker(self, value: str, value_type: str) -> str:
        if isinstance(value, int):
            value = str(value)
        if not re.match(r"\d+", value) and value != "*":
            raise ValueError(
                f"{value_type} in the incorrect format. Make sure to have it as a number"
            )
        return value

    def __str__(self):
        return f"{self.field_name}:[{self.from_value} TO {self.to_value}]"

    def __new__(cls, *args, **kwargs):
        """Create the field and return it wrapped in a QueryBuilder."""
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return QueryBuilder([instance])


class XRefCountField:

    def __init__(self, field_name, from_value, to_value):
        self.field_name = self._xref_check(field_name)
        self.from_value = from_value
        self.to_value = to_value

    def _xref_check(self, xref):
        xref = xref.replace("xref_", "") if xref.startswith("xref_") else xref
        if xref not in XREF_FIELDS:
            raise ValueError(
                f"{xref} is not a valid field. Please check the available fields: \n {XREF_FIELDS}"
            )
        return xref

    def __str__(self):
        return f"xref_count_{self.field_name}:[{self.from_value} TO {self.to_value}]"

    def __new__(cls, *args, **kwargs):
        """Create the field and return it wrapped in a QueryBuilder."""
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return QueryBuilder([instance])


AnyField = Union[
    BooleanField, DateRangeField, QuoteField, RangeField, SimpleField, XRefCountField
]
