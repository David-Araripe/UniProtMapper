# -*- coding: utf-8 -*-
import json
import time
import unittest
from pathlib import Path

import requests
from UniProtMapper import SwissProtParser, UniProtIDMapper

# Load the mock response from the JSON file
r_root = Path(__file__).parent / "resources"
with open(r_root / "A3_mock_IDMapper_response.json", "r") as f:
    mock_response = json.load(f)


class TestUniprotMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = UniProtIDMapper()
        self.parser = SwissProtParser()
        self.supported_dbs = self.mapper._supported_dbs
        self.supported_crossrefs = self.parser._supported_crossrefs
        self.supported_uniprot_fields = self.parser._supported_fields
        r_root = Path(__file__).parent / "resources"
        self.expected_r_types = json.loads(
            (r_root / "A1_response_types.json").read_text()
        )

    def test_mapIDs(self):
        uniprot_ids = "P30542"
        result, failed = self.mapper.mapIDs(uniprot_ids)
        self.assertEqual(result.loc[0, "to"]["primaryAccession"], uniprot_ids)

    def test_all_supported_dbs(self):
        uniprot_ids = "P30542"
        retrieved_results = {}
        failed_results = {}
        exeption_dict = {}
        # avoid mapping from Uniprot to Uniprot.
        dbs_subset = [db for db in self.supported_dbs if db != "UniProtKB_AC-ID"]
        for db in dbs_subset:
            try:
                result, failed = self.mapper.mapIDs(uniprot_ids, to_db=db)
                time.sleep(0.5)
            except requests.RequestException as e:
                exeption_dict.update({db: e})
                continue
            if failed is not None:
                failed_results.update({db: failed})
            if not result.empty:
                retrieved_results.update({db: result.loc[0, "to"]})
        for r_key in retrieved_results.keys():
            if r_key in self.expected_r_types["as_dictionary"]:
                self.assertTrue(isinstance(retrieved_results[r_key], dict))
            elif r_key in self.expected_r_types["as_string"]:
                self.assertTrue(isinstance(retrieved_results[r_key], str))
            else:
                raise ValueError(f"Unexpected result type for {r_key}")

    def test_mapIDs_not_found(self):
        uniprot_ids = "PXXXXX"
        result, failed = self.mapper.mapIDs(uniprot_ids)
        self.assertTrue(result.empty)
        self.assertEqual(failed, [uniprot_ids])

    def test_mapIDs_multiple(self):
        uniprot_ids = "P30542"
        result, failed = self.mapper.mapIDs(uniprot_ids)
        self.assertEqual(len(result), 1)

    def test_mapIDs_multiple_not_found(self):
        uniprot_ids = ["yolo", "haha", "inexistent"]
        result, failed = self.mapper.mapIDs(uniprot_ids)
        self.assertTrue(result.empty)
        self.assertEqual(failed, uniprot_ids)

    def tearDown(self) -> None:
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
