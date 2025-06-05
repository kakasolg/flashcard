from datetime import datetime, timedelta

class SpacedRepetitionEngine:
    """
    A simple Spaced Repetition System (SRS) engine.
    """
    # Define the custom review intervals
    # In a real application, these might be more configurable or based on learning science.
    # For this task, we'll use fixed intervals: 1 hour, 3 hours, 24 hours, 3 days, 7 days.
    CUSTOM_INTERVALS = {
        "1_hour": timedelta(hours=1),
        "3_hours": timedelta(hours=3),
        "24_hours": timedelta(hours=24),
        "3_days": timedelta(days=3),
        "7_days": timedelta(days=7),
    }

    def __init__(self, current_interval_key: str = "1_hour"):
        """
        Initializes the SRS engine.

        Args:
            current_interval_key: The key for the current review interval.
                                  Defaults to "1_hour" for a new card.
        """
        if current_interval_key not in self.CUSTOM_INTERVALS:
            raise ValueError(f"Invalid interval key: {current_interval_key}. "
                             f"Allowed keys are: {list(self.CUSTOM_INTERVALS.keys())}")
        self.current_interval_key = current_interval_key

    def schedule_next_review(self, ease_of_recall: str, chosen_interval_key: str = None) -> datetime:
        """
        Schedules the next review date for a flashcard based on ease of recall
        and an optional chosen custom interval.

        Args:
            ease_of_recall: How well the user recalled the card.
                            Expected values: "easy", "medium", "hard".
                            (This is a simplified model for now)
            chosen_interval_key: The key for the user-chosen custom interval from CUSTOM_INTERVALS.
                                 If None, the engine will try to determine the next interval
                                 based on ease_of_recall (simplified for now).

        Returns:
            The datetime for the next scheduled review.
        """
        now = datetime.now()

        if chosen_interval_key:
            if chosen_interval_key not in self.CUSTOM_INTERVALS:
                raise ValueError(f"Invalid chosen interval key: {chosen_interval_key}. "
                                 f"Allowed keys are: {list(self.CUSTOM_INTERVALS.keys())}")
            # User has chosen a specific interval
            self.current_interval_key = chosen_interval_key
            next_review_date = now + self.CUSTOM_INTERVALS[self.current_interval_key]
        else:
            # Simplified logic if no specific interval is chosen by the user.
            # A real SRS would have more complex logic to advance intervals.
            if ease_of_recall == "easy":
                # Advance to the next interval if possible
                current_index = list(self.CUSTOM_INTERVALS.keys()).index(self.current_interval_key)
                if current_index < len(self.CUSTOM_INTERVALS) - 1:
                    self.current_interval_key = list(self.CUSTOM_INTERVALS.keys())[current_index + 1]
                else:
                    # Already at the longest interval, keep it there or cap it.
                    pass # Stays at 7_days for this simplified model
            elif ease_of_recall == "medium":
                # Keep the same interval
                pass
            elif ease_of_recall == "hard":
                # Reset to the shortest interval (or a shorter one)
                self.current_interval_key = "1_hour"
            else:
                raise ValueError(f"Invalid ease_of_recall: {ease_of_recall}. "
                                 "Expected 'easy', 'medium', or 'hard'.")

            next_review_date = now + self.CUSTOM_INTERVALS[self.current_interval_key]

        return next_review_date

    def get_available_intervals(self) -> dict:
        """
        Returns the dictionary of available custom intervals.
        """
        return self.CUSTOM_INTERVALS

# Example Usage (can be removed or moved to a test file later)
if __name__ == "__main__":
    engine = SpacedRepetitionEngine()
    print(f"Available intervals: {engine.get_available_intervals()}")

    # Scenario 1: User chooses a specific interval
    next_review_custom = engine.schedule_next_review(ease_of_recall="easy", chosen_interval_key="3_hours")
    print(f"Next review (custom '3_hours'): {next_review_custom}, Current engine interval: {engine.current_interval_key}")

    # Scenario 2: Engine determines interval based on "easy"
    # Assuming previous state was "3_hours" due to above call
    next_review_easy = engine.schedule_next_review(ease_of_recall="easy")
    print(f"Next review (easy): {next_review_easy}, Current engine interval: {engine.current_interval_key}") # Should advance

    # Scenario 3: Engine determines interval based on "hard"
    next_review_hard = engine.schedule_next_review(ease_of_recall="hard")
    print(f"Next review (hard): {next_review_hard}, Current engine interval: {engine.current_interval_key}") # Should reset

    # Scenario 4: User chooses "7_days" and then recalls "easy"
    engine_2 = SpacedRepetitionEngine(current_interval_key="3_days")
    next_review_custom_long = engine_2.schedule_next_review(ease_of_recall="easy", chosen_interval_key="7_days")
    print(f"Next review (custom '7_days'): {next_review_custom_long}, Current engine interval: {engine_2.current_interval_key}")
    next_review_easy_after_long = engine_2.schedule_next_review(ease_of_recall="easy")
    print(f"Next review (easy after '7_days'): {next_review_easy_after_long}, Current engine interval: {engine_2.current_interval_key}") # Should stay at 7_days

    # Scenario 5: Invalid interval key
    try:
        engine.schedule_next_review(ease_of_recall="easy", chosen_interval_key="invalid_key")
    except ValueError as e:
        print(f"Error caught as expected: {e}")

    # Scenario 6: Invalid ease_of_recall
    try:
        engine.schedule_next_review(ease_of_recall="very_hard")
    except ValueError as e:
        print(f"Error caught as expected: {e}")

    # Scenario 7: Initializing with an invalid key
    try:
        SpacedRepetitionEngine(current_interval_key="bad_key")
    except ValueError as e:
        print(f"Error caught for init: {e}")

# Example Usage (can be removed or moved to a test file later)
# if __name__ == "__main__":
#     engine = SpacedRepetitionEngine()
#     print(f"Available intervals: {engine.get_available_intervals()}")

#     # Scenario 1: User chooses a specific interval
#     next_review_custom = engine.schedule_next_review(ease_of_recall="easy", chosen_interval_key="3_hours")
#     print(f"Next review (custom '3_hours'): {next_review_custom}, Current engine interval: {engine.current_interval_key}")

#     # Scenario 2: Engine determines interval based on "easy"
#     # Assuming previous state was "3_hours" due to above call
#     next_review_easy = engine.schedule_next_review(ease_of_recall="easy")
#     print(f"Next review (easy): {next_review_easy}, Current engine interval: {engine.current_interval_key}") # Should advance

#     # Scenario 3: Engine determines interval based on "hard"
#     next_review_hard = engine.schedule_next_review(ease_of_recall="hard")
#     print(f"Next review (hard): {next_review_hard}, Current engine interval: {engine.current_interval_key}") # Should reset

#     # Scenario 4: User chooses "7_days" and then recalls "easy"
#     engine_2 = SpacedRepetitionEngine(current_interval_key="3_days")
#     next_review_custom_long = engine_2.schedule_next_review(ease_of_recall="easy", chosen_interval_key="7_days")
#     print(f"Next review (custom '7_days'): {next_review_custom_long}, Current engine interval: {engine_2.current_interval_key}")
#     next_review_easy_after_long = engine_2.schedule_next_review(ease_of_recall="easy")
#     print(f"Next review (easy after '7_days'): {next_review_easy_after_long}, Current engine interval: {engine_2.current_interval_key}") # Should stay at 7_days

#     # Scenario 5: Invalid interval key
#     try:
#         engine.schedule_next_review(ease_of_recall="easy", chosen_interval_key="invalid_key")
#     except ValueError as e:
#         print(f"Error caught as expected: {e}")

#     # Scenario 6: Invalid ease_of_recall
#     try:
#         engine.schedule_next_review(ease_of_recall="very_hard")
#     except ValueError as e:
#         print(f"Error caught as expected: {e}")

#     # Scenario 7: Initializing with an invalid key
#     try:
#         SpacedRepetitionEngine(current_interval_key="bad_key")
#     except ValueError as e:
#         print(f"Error caught for init: {e}")
