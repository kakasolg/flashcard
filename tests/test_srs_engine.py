import unittest
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory (project root) to the Python path
# to allow importing from the 'core' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.srs_engine import SpacedRepetitionEngine

class TestSpacedRepetitionEngine(unittest.TestCase):

    def assertAlmostEqualTimedelta(self, td1, td2, delta_seconds=1):
        """Helper to compare timedeltas with a small tolerance."""
        self.assertTrue(abs((td1 - td2).total_seconds()) < delta_seconds,
                        f"{td1} and {td2} are not almost equal.")

    def test_initialization(self):
        engine = SpacedRepetitionEngine()
        self.assertEqual(engine.current_interval_key, "1_hour")

        engine_custom = SpacedRepetitionEngine(current_interval_key="3_days")
        self.assertEqual(engine_custom.current_interval_key, "3_days")

        with self.assertRaises(ValueError):
            SpacedRepetitionEngine(current_interval_key="invalid_interval")

    def test_get_available_intervals(self):
        engine = SpacedRepetitionEngine()
        intervals = engine.get_available_intervals()
        self.assertEqual(intervals, SpacedRepetitionEngine.CUSTOM_INTERVALS)
        self.assertIn("1_hour", intervals)
        self.assertIn("7_days", intervals)

    def test_schedule_with_chosen_interval(self):
        engine = SpacedRepetitionEngine()
        now = datetime.now()

        # Test choosing each available interval
        for key, duration in SpacedRepetitionEngine.CUSTOM_INTERVALS.items():
            next_review = engine.schedule_next_review(ease_of_recall="easy", chosen_interval_key=key)
            self.assertEqual(engine.current_interval_key, key)
            # Using a small delta for time comparison due to execution time
            self.assertAlmostEqual((next_review - now).total_seconds(), duration.total_seconds(), delta=1)

        with self.assertRaises(ValueError):
            engine.schedule_next_review(ease_of_recall="easy", chosen_interval_key="non_existent_key")

    def test_schedule_engine_determines_easy(self):
        engine = SpacedRepetitionEngine(current_interval_key="1_hour")
        now = datetime.now()

        # Easy from 1_hour should go to 3_hours
        next_review = engine.schedule_next_review(ease_of_recall="easy")
        self.assertEqual(engine.current_interval_key, "3_hours")
        self.assertAlmostEqualTimedelta(next_review, now + SpacedRepetitionEngine.CUSTOM_INTERVALS["3_hours"])

        # Easy from 3_hours should go to 24_hours
        next_review = engine.schedule_next_review(ease_of_recall="easy")
        self.assertEqual(engine.current_interval_key, "24_hours")
        self.assertAlmostEqualTimedelta(next_review, now + SpacedRepetitionEngine.CUSTOM_INTERVALS["24_hours"])

        # ...and so on, until the last interval
        engine.current_interval_key = "3_days"
        next_review = engine.schedule_next_review(ease_of_recall="easy")
        self.assertEqual(engine.current_interval_key, "7_days")
        self.assertAlmostEqualTimedelta(next_review, now + SpacedRepetitionEngine.CUSTOM_INTERVALS["7_days"])

        # Easy from 7_days (longest) should stay at 7_days
        next_review = engine.schedule_next_review(ease_of_recall="easy")
        self.assertEqual(engine.current_interval_key, "7_days")
        self.assertAlmostEqualTimedelta(next_review, now + SpacedRepetitionEngine.CUSTOM_INTERVALS["7_days"])


    def test_schedule_engine_determines_medium(self):
        engine = SpacedRepetitionEngine(current_interval_key="3_hours")
        now = datetime.now()

        # Medium should keep the current interval
        next_review = engine.schedule_next_review(ease_of_recall="medium")
        self.assertEqual(engine.current_interval_key, "3_hours")
        self.assertAlmostEqualTimedelta(next_review, now + SpacedRepetitionEngine.CUSTOM_INTERVALS["3_hours"])

        engine.current_interval_key = "7_days"
        next_review = engine.schedule_next_review(ease_of_recall="medium")
        self.assertEqual(engine.current_interval_key, "7_days")
        self.assertAlmostEqualTimedelta(next_review, now + SpacedRepetitionEngine.CUSTOM_INTERVALS["7_days"])

    def test_schedule_engine_determines_hard(self):
        engine = SpacedRepetitionEngine(current_interval_key="3_days")
        now = datetime.now()

        # Hard should reset to the shortest interval ("1_hour")
        next_review = engine.schedule_next_review(ease_of_recall="hard")
        self.assertEqual(engine.current_interval_key, "1_hour")
        self.assertAlmostEqualTimedelta(next_review, now + SpacedRepetitionEngine.CUSTOM_INTERVALS["1_hour"])

        engine.current_interval_key = "7_days" # Even from the longest interval
        next_review = engine.schedule_next_review(ease_of_recall="hard")
        self.assertEqual(engine.current_interval_key, "1_hour")
        self.assertAlmostEqualTimedelta(next_review, now + SpacedRepetitionEngine.CUSTOM_INTERVALS["1_hour"])

    def test_schedule_invalid_ease_of_recall(self):
        engine = SpacedRepetitionEngine()
        with self.assertRaises(ValueError):
            engine.schedule_next_review(ease_of_recall="very_easy") # Invalid ease

# if __name__ == "__main__":
#     unittest.main()
