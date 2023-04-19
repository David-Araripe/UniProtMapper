# -*- coding: utf-8 -*-
import json
import unittest
from pathlib import Path

from UniProtMapper.utils import (
    search_comments,
    search_keys_inlist,
    search_uniprot_crossrefs,
)


class TestUtils(unittest.TestCase):
    def setUp(self):
        """Load test data from the resources folder."""
        r_root = Path(__file__).parent / "resources"
        self.list_of_dicts = json.loads((r_root / "list_of_dicts.json").read_text())
        self.dict_comments = json.loads((r_root / "dict_comments.json").read_text())
        self.mock_crossref = json.loads((r_root / "mock_crossref.json").read_text())

    def test_search_keys_inlist(self):
        desiredkey = "key1"
        self.assertEqual(search_keys_inlist(self.list_of_dicts, desiredkey), "value1")

        desiredkey = "key2"
        self.assertEqual(search_keys_inlist(self.list_of_dicts, desiredkey), "value2")

        desiredkey = "key3"
        self.assertEqual(search_keys_inlist(self.list_of_dicts, desiredkey), "value3")

        desiredkey = "key4"
        self.assertEqual(search_keys_inlist(self.list_of_dicts, desiredkey), "value4")

    def test_search_comments(self):
        comment_type = "type1"
        self.assertEqual(
            search_comments(self.dict_comments, comment_type),
            {"commentType": "type1", "comment": "value1"},
        )

        comment_type = "type2"
        self.assertEqual(
            search_comments(self.dict_comments, comment_type),
            {"commentType": "type2", "comment": "value2"},
        )

    def test_search_uniprot_crossrefs(self):
        target_dbs = ["database1", "database2"]
        self.assertEqual(
            search_uniprot_crossrefs(self.mock_crossref, target_dbs),
            {"database1": ["id1~key1~value1"], "database2": ["id2~key2~value2"]},
        )


if __name__ == "__main__":
    unittest.main()
