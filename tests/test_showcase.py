"""Layout checks; runtime accessibility and trading are recorded separately."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_showcase import PLOTS, plan


class ShowcaseTests(unittest.TestCase):
    def test_all_five_shops_are_separate_and_compact(self):
        self.assertEqual(5, len({p["style"] for p in PLOTS}))
        for left, right in zip(PLOTS, PLOTS[1:]):
            self.assertLess(left["x"] + left["width"], right["x"])
        self.assertLessEqual(PLOTS[-1]["x"] + PLOTS[-1]["width"] - PLOTS[0]["x"], 110)

    def test_build_finishes_in_survival_with_supplies_not_free_tea(self):
        commands = plan()
        self.assertEqual("gamemode survival", commands[-1])
        self.assertEqual(5, sum(c.startswith("place template") for c in commands))
        self.assertFalse(any(c.startswith("give") for c in commands))
        self.assertTrue(any("advance_weather false" in c for c in commands))


if __name__ == "__main__":
    unittest.main()
