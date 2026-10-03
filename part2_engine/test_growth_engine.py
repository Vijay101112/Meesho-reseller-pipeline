"""Given-When-Then tests for growth_engine.  Run: python -m unittest -v (from part2_engine/)."""
import csv
import os
import unittest

from growth_engine import is_flagged, mom_growth, validate_feed

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")
MONTHLY = os.path.join(FIX, "monthly_category_revenue.csv")
CORRUPTED = os.path.join(FIX, "corrupted_feed.csv")


def load_revenue():
    data = {}
    with open(MONTHLY, newline="") as f:
        for r in csv.DictReader(f):
            data[(r["month"], r["category"])] = float(r["revenue"])
    return data


class TestGrowthEngine(unittest.TestCase):
    def test_may_ethnic_wear_is_flagged(self):
        # GIVEN Ethnic Wear moves 104520.77 -> 185107.61 (April -> May)
        prev, cur = 104520.77, 185107.61
        # WHEN mom_growth then is_flagged run
        pct = mom_growth(prev, cur)
        # THEN 77.1 and "flagged"
        self.assertEqual(pct, 77.1)
        self.assertEqual(is_flagged(pct), "flagged")

    def test_june_beauty_is_not_flagged(self):
        # GIVEN Beauty & Personal Care moves 35542.11 -> 37559.07 (May -> June)
        pct = mom_growth(35542.11, 37559.07)
        # THEN 5.67 and "not_flagged"
        self.assertEqual(pct, 5.67)
        self.assertEqual(is_flagged(pct), "not_flagged")

    def test_exact_boundary_is_escalated(self):
        # GIVEN previous=100000, current=108000 (exactly 8%)
        pct = mom_growth(100000, 108000)
        # THEN exactly 8.0 and "escalate_exact_boundary" (neither flagged nor not_flagged)
        self.assertEqual(pct, 8.0)
        self.assertEqual(is_flagged(pct), "escalate_exact_boundary")
        self.assertEqual(is_flagged(-8.0), "escalate_exact_boundary")

    def test_corrupted_feed_returns_three_ordered_errors(self):
        # GIVEN the corrupted feed fixture
        # WHEN validate_feed runs
        ok, errors = validate_feed(CORRUPTED)
        # THEN (False, 3 errors) in file order
        self.assertFalse(ok)
        self.assertEqual(errors, [
            "line 3: negative revenue (-4200.0) for category=Western Wear",
            "line 4: missing category (month=July)",
            "line 6: missing revenue (category=Home & Kitchen)",
        ])

    def test_validated_part1_output_passes(self):
        # GIVEN the Part 1 monthly feed (15 rows)  WHEN validated  THEN (True, [])
        self.assertEqual(validate_feed(MONTHLY), (True, []))

    def test_non_numeric_revenue_is_reported(self):
        # GIVEN a feed with revenue "abc"  WHEN validated  THEN a 'not numeric' error
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as t:
            t.write("month,category,revenue,n_orders\nJuly,Kids Wear,abc,5\n")
        try:
            ok, errors = validate_feed(t.name)
        finally:
            os.remove(t.name)
        self.assertFalse(ok)
        self.assertEqual(errors, ["line 2: revenue not numeric: 'abc'"])

    def test_zero_previous_revenue_raises(self):
        # GIVEN previous=0  WHEN mom_growth  THEN ValueError instead of a bogus number
        with self.assertRaises(ValueError):
            mom_growth(0, 100)

    def test_full_mom_tables(self):
        # GIVEN real Part 1 revenue  WHEN MoM computed for each category
        rev = load_revenue()
        cats = ["Ethnic Wear", "Western Wear", "Kids Wear", "Home & Kitchen", "Beauty & Personal Care"]
        may = {c: mom_growth(rev[("April", c)], rev[("May", c)]) for c in cats}
        june = {c: mom_growth(rev[("May", c)], rev[("June", c)]) for c in cats}
        # THEN they equal the brief's tables
        self.assertEqual(may, {"Ethnic Wear": 77.1, "Western Wear": -23.6, "Kids Wear": -23.48,
                               "Home & Kitchen": -9.25, "Beauty & Personal Care": -12.75})
        self.assertEqual(june, {"Ethnic Wear": -58.74, "Western Wear": 11.97, "Kids Wear": 23.9,
                                "Home & Kitchen": 42.59, "Beauty & Personal Care": 5.67})
        self.assertTrue(all(is_flagged(v) == "flagged" for v in may.values()))
        self.assertEqual(sum(is_flagged(v) == "flagged" for v in june.values()), 4)


if __name__ == "__main__":
    unittest.main()
