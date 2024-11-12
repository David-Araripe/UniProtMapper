import unittest

import pandas as pd

from UniProtMapper.uniprotkb_api import ProtKB
from UniProtMapper.uniprotkb_fields import accession
from UniProtMapper.utils import read_fields_table


class TestProtKB(unittest.TestCase):
    """Tests for the ProtKB class using baseline data from real API responses."""

    @classmethod
    def setUpClass(cls):
        cls.test_ids = ["P30542", "Q16678", "Q02880"]

        protkb = ProtKB()
        cls.query = accession("P30542") | accession("Q16678") | accession("Q02880")

        # Get baseline data with default fields
        cls.baseline_default = protkb.get(cls.query)

        # Get baseline data with custom fields
        cls.custom_fields = [
            "accession",
            "id",
            "organism_name",
            "go_id",
            "go_p",
            "go_c",
            "go_f",
            "gene_names",
            "protein_name",
        ]
        cls.baseline_custom = protkb.get(cls.query, fields=cls.custom_fields)

        # Save baseline data to class variables
        cls.default_columns = cls.baseline_default.columns.tolist()
        cls.custom_columns = cls.baseline_custom.columns.tolist()

    def setUp(self):
        """Set up test fixtures before each test."""
        self.protkb = ProtKB()

    def test_default_fields_retrieval(self):
        """Test retrieval with default fields matches baseline."""
        result = self.protkb.get(self.query)

        # Verify structure
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), len(self.test_ids))

        # Verify columns match baseline
        self.assertEqual(set(result.columns), set(self.default_columns))

        # Verify content matches baseline
        pd.testing.assert_frame_equal(
            result.sort_values("Entry").reset_index(drop=True),
            self.baseline_default.sort_values("Entry").reset_index(drop=True),
            check_exact=True,
        )

    def test_custom_fields_retrieval(self):
        """Test retrieval with custom fields matches baseline."""
        result = self.protkb.get(self.query, fields=self.custom_fields)

        # Verify structure
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), len(self.test_ids))

        # Verify columns match baseline
        self.assertEqual(set(result.columns), set(self.custom_columns))

        # Verify content matches baseline
        pd.testing.assert_frame_equal(
            result.sort_values("Entry").reset_index(drop=True),
            self.baseline_custom.sort_values("Entry").reset_index(drop=True),
            check_exact=True,
        )

    def test_invalid_field(self):
        """Test that invalid fields raise appropriate errors."""
        with self.assertRaises(Exception):  # Adjust exception type as needed
            self.protkb.get(self.query, fields=["invalid_field"])

    def test_field_content(self):
        """Test specific content of retrieved data."""
        result = self.protkb.get(self.query)

        # Verify all test IDs are present
        retrieved_accessions = result["Entry"].tolist()
        for acc in self.test_ids:
            self.assertIn(acc, retrieved_accessions)

        # Verify specific content for known entries
        p30542_data = result[result["Entry"] == "P30542"].iloc[0]
        self.assertTrue("ADORA1" in str(p30542_data["Gene Names"]))
        self.assertTrue("Homo sapiens" in str(p30542_data["Organism"]))

    def test_format_specifications(self):
        """Test different format specifications."""

        # Test TSV format (default)
        result_tsv = self.protkb.get(self.query, format="tsv")
        self.assertIsInstance(result_tsv, pd.DataFrame)

        # Test JSON format
        result_json = self.protkb.get(self.query, format="json")
        self.assertIsInstance(result_json, pd.DataFrame)

        # Verify both formats return same number of entries
        self.assertEqual(len(result_tsv), len(result_json))

    def test_response_field_compatibility(self):
        """Test that all the retrieved data is the one expected from the fields table."""
        result = self.protkb.get(self.query)

        self.assertEqual(len(result), len(self.test_ids))  # all entries retrieved
        self.assertEqual(len(result), len(result["Entry"].unique()))  # no duplicates

        # check that all columns in the results are in the fields table
        returned_cols = read_fields_table()["label"].values
        for col in result.columns:
            self.assertTrue(col in returned_cols)


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
