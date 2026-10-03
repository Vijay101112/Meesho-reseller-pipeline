"""Run from part3_narrative/:  python -m unittest -v"""
import csv
import os
import re
import unittest

from masking import alias_for, assert_no_raw_names_leak
from prompt_pack import draft_message, numbers_trace

HERE = os.path.dirname(os.path.abspath(__file__))


def raw_names():
    with open(os.path.join(HERE, "..", "data", "resellers.csv"), newline="") as f:
        return [r["reseller_name"] for r in csv.DictReader(f)]


def top_reseller_block():
    with open(os.path.join(HERE, "narrative_report.md"), encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"<!-- TOP_RESELLER_NARRATIVE_START -->(.*?)<!-- TOP_RESELLER_NARRATIVE_END -->", text, re.S)
    return m.group(1)


class TestMasking(unittest.TestCase):
    def test_alias(self):
        self.assertEqual(alias_for("RS019"), "ALIAS-19")
        self.assertEqual(alias_for("RS006"), "ALIAS-06")

    def test_final_narrative_has_no_leak(self):
        block = top_reseller_block()
        self.assertTrue(assert_no_raw_names_leak(block, raw_names()))
        for rid in ["RS019", "RS022", "RS012", "RS006", "RS005"]:
            self.assertIn(alias_for(rid), block)

    def test_negative_case_detects_leak(self):
        leaky = top_reseller_block() + " Mumbai Reseller 1 led the list."
        self.assertFalse(assert_no_raw_names_leak(leaky, raw_names()))

    def test_draft_message_numbers_trace(self):
        msg = draft_message("Ethnic Wear", 104520.77, 185107.61, 77.1, "May", "April")
        self.assertTrue(numbers_trace(msg, ["104520.77", "185107.61", "77.1"]))
        self.assertFalse(numbers_trace(msg + " 99", ["104520.77", "185107.61", "77.1"]))


if __name__ == "__main__":
    unittest.main()
