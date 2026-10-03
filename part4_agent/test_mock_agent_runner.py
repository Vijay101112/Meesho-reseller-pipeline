"""Agent-level Given-When-Then specs.  Run from part4_agent/:  python -m unittest -v"""
import os
import re
import unittest

from mock_agent_runner import run

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FEED = os.path.join(ROOT, "part2_engine", "fixtures", "monthly_category_revenue.csv")
BAD = os.path.join(ROOT, "part2_engine", "fixtures", "corrupted_feed.csv")
KEYS = ["run_month", "validation_status", "validation_errors", "flagged_categories",
        "suppressed_categories", "escalated_categories", "action_taken"]


class TestAgent(unittest.TestCase):
    def test_may_scenario(self):
        r = run("May", FEED, FEED)
        self.assertEqual(list(r), KEYS)
        self.assertEqual(r["validation_status"], "valid")
        self.assertEqual([(e["category"], e["mom_pct"]) for e in r["flagged_categories"]],
                         [("Ethnic Wear", 77.1), ("Western Wear", -23.6), ("Kids Wear", -23.48)])
        self.assertTrue(all(e["drafted"] for e in r["flagged_categories"]))
        self.assertEqual(sorted(r["suppressed_categories"]), ["Beauty & Personal Care", "Home & Kitchen"])
        self.assertEqual(r["escalated_categories"], [])
        self.assertEqual(r["action_taken"], "drafted_and_held_for_approval")

    def test_june_scenario(self):
        r = run("June", FEED, FEED)
        self.assertEqual([(e["category"], e["mom_pct"]) for e in r["flagged_categories"]],
                         [("Ethnic Wear", -58.74), ("Home & Kitchen", 42.59), ("Kids Wear", 23.9)])
        self.assertEqual(r["suppressed_categories"], ["Western Wear"])
        everything = [e["category"] for e in r["flagged_categories"]] + r["suppressed_categories"]
        self.assertNotIn("Beauty & Personal Care", everything)  # 5.67% was never flagged
        self.assertEqual(r["escalated_categories"], [])

    def test_corrupted_feed_is_hard_stop(self):
        r = run("July", FEED, BAD)
        self.assertEqual(list(r), KEYS)
        self.assertEqual(r["validation_status"], "invalid")
        self.assertEqual(r["action_taken"], "hard_stop")
        self.assertEqual(r["validation_errors"], [
            "line 3: negative revenue (-4200.0) for category=Western Wear",
            "line 4: missing category (month=July)",
            "line 6: missing revenue (category=Home & Kitchen)"])
        self.assertEqual(r["flagged_categories"], [])
        self.assertEqual(r["suppressed_categories"], [])
        self.assertEqual(r["escalated_categories"], [])

    def test_every_message_number_traces(self):
        for month in ["May", "June"]:
            for e in run(month, FEED, FEED)["flagged_categories"]:
                nums = set(re.findall(r"-?\d+(?:\.\d+)?", e["message"]))
                allowed = {f"{e['previous_revenue']:.2f}", f"{e['current_revenue']:.2f}", str(e["mom_pct"])}
                self.assertEqual(nums, allowed)
                self.assertIn(e["category"], e["message"])
                self.assertEqual(e["approval_status"], "pending_human_review")

    def test_exact_boundary_is_escalated_not_dropped(self):
        # GIVEN a 100000 -> 108000 category (exactly 8.0%)
        import tempfile
        p = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="")
        p.write("month,category,revenue,n_orders\nApril,Kids Wear,100000.00,10\nMay,Kids Wear,108000.00,11\n")
        p.close()
        try:
            r = run("May", p.name, p.name)
        finally:
            os.remove(p.name)
        # THEN it is escalated, and appears in neither flagged nor suppressed
        self.assertEqual(r["escalated_categories"], ["Kids Wear"])
        self.assertEqual(r["flagged_categories"], [])
        self.assertEqual(r["suppressed_categories"], [])


if __name__ == "__main__":
    unittest.main()
