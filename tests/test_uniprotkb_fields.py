import unittest

from UniProtMapper.field_base_classes import QueryBuilder
from UniProtMapper.uniprotkb_fields import (
    accession,
    date_created,
    length,
    mass,
    organism_name,
    protein_name,
    reviewed,
    xref_count,
)


class TestQueryBuilder(unittest.TestCase):
    def test_simple_query(self):
        # Test single field query
        query = accession("P12345")
        self.assertIsInstance(query, QueryBuilder)
        self.assertEqual(str(query), "accession:P12345")

    def test_and_operator(self):
        # Test AND operation between two queries
        query = reviewed(True) & accession("P12345")
        self.assertEqual(str(query), "reviewed:true AND accession:P12345")

    def test_or_operator(self):
        # Test OR operation between two queries
        query = accession("P12345") | accession("Q67890")
        self.assertEqual(str(query), "accession:P12345 OR accession:Q67890")

    def test_not_operator(self):
        # Test NOT operation
        query = ~reviewed(True)
        self.assertEqual(str(query), "NOT reviewed:true")

    def test_complex_query(self):
        # Test complex query with multiple operators
        query = reviewed(True) & (organism_name("human") | organism_name("mouse"))
        self.assertEqual(
            str(query),
            "reviewed:true AND(organism_name:'human' OR organism_name:'mouse')",
        )

    def test_nested_query(self):
        # Test nested query with multiple levels
        query = ~(reviewed(True) & accession("P12345")) | organism_name("human")
        self.assertEqual(
            str(query),
            "(NOT(reviewed:true AND accession:P12345)) OR organism_name:'human'",
        )

    def test_invalid_operations(self):
        # Test invalid operations
        query = accession("P12345")
        with self.assertRaises(TypeError):
            query & "invalid"
        with self.assertRaises(TypeError):
            query | 123


class TestFieldTypes(unittest.TestCase):
    def test_boolean_field(self):
        field = reviewed(True)
        self.assertEqual(str(field), "reviewed:true")
        field = reviewed(False)
        self.assertEqual(str(field), "reviewed:false")

    def test_simple_field(self):
        field = accession("P12345")
        self.assertEqual(str(field), "accession:P12345")

    def test_quote_field(self):
        field = protein_name("kinase")
        self.assertEqual(str(field), "protein_name:'kinase'")
        field = organism_name("Homo sapiens")
        self.assertEqual(str(field), "organism_name:'Homo sapiens'")

    def test_date_range_field(self):
        # Test with actual dates
        field = date_created("2020-01-01", "2020-12-31")
        self.assertEqual(str(field), "date_created:[2020-01-01 TO 2020-12-31]")

        # Test with wildcard
        field = date_created("2020-01-01", "*")
        self.assertEqual(str(field), "date_created:[2020-01-01 TO *]")

        # Test invalid date format
        with self.assertRaises(ValueError):
            date_created("2020/01/01", "2020-12-31")

    def test_range_field(self):
        # Test with integers
        field = length(100, 200)
        self.assertEqual(str(field), "length:[100 TO 200]")

        # Test with strings
        field = mass("1000", "2000")
        self.assertEqual(str(field), "mass:[1000 TO 2000]")

        # Test with wildcard
        field = length(100, "*")
        self.assertEqual(str(field), "length:[100 TO *]")

        # Test invalid range
        with self.assertRaises(ValueError):
            length("invalid", 200)

    def test_xref_count_field(self):
        # Test valid xref field
        field = xref_count("pdb", 1, 5)
        self.assertEqual(str(field), "xref_count_pdb:[1 TO 5]")

        # Test invalid xref field
        with self.assertRaises(ValueError):
            xref_count("invalid_xref", 1, 5)


class TestComplexQueryBuilder(unittest.TestCase):

    def test_deeply_nested_queries(self):
        # Testing deep nesting with multiple NOT operations
        query = ~(
            reviewed(True)
            & ~(
                organism_name("human")
                | ~(length(100, 200) & ~(mass(1000, 2000) | accession("P12345")))
            )
        )

        expected = (
            "NOT(reviewed:true AND"
            "(NOT(organism_name:'human' OR"
            "(NOT(length:[100 TO 200] AND"
            "(NOT(mass:[1000 TO 2000] OR "
            "accession:P12345)))))))"
        )

        self.assertEqual(str(query), expected)

    def test_multiple_or_and_combinations(self):
        # Testing complex combinations of OR and AND with different precedence
        a = reviewed(True)
        b = organism_name("human")
        c = length(100, 200)
        d = mass(1000, 2000)
        e = accession("P12345")

        query = (a & b) | (c & (d | e))

        expected = (
            "(reviewed:true AND organism_name:'human') OR"
            + "(length:[100 TO 200] AND(mass:[1000 TO 2000] OR accession:P12345))"
        )

        self.assertEqual(str(query), expected)

    def test_chained_operations(self):

        query = (
            (reviewed(True) & organism_name("human"))
            | (organism_name("mouse") & length(100, 200))
            | (mass(1000, 2000) & accession("P12345"))
            | protein_name("kinase")
        )

        expected = (
            "(reviewed:true AND organism_name:'human') OR"
            + "(organism_name:'mouse' AND length:[100 TO 200]) OR"
            + "(mass:[1000 TO 2000] AND accession:P12345) OR "
            + "protein_name:'kinase'"
        )

        self.assertEqual(str(query), expected)


if __name__ == "__main__":
    unittest.main()
