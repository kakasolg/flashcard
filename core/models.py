from datetime import datetime

class Flashcard:
    """
    Represents a single flashcard.
    """
    def __init__(self, card_id: str, question: str, answer: str,
                 creation_date: datetime = None,
                 last_reviewed_date: datetime = None,
                 next_review_date: datetime = None,
                 current_interval_key: str = "1_hour", # Matches a key in SpacedRepetitionEngine.CUSTOM_INTERVALS
                 ease_history: list = None): # List of ease assessments ("easy", "medium", "hard")
        """
        Initializes a Flashcard object.

        Args:
            card_id: A unique identifier for the card.
            question: The question or front side of the card.
            answer: The answer or back side of the card.
            creation_date: The date the card was created. Defaults to now.
            last_reviewed_date: The date the card was last reviewed.
            next_review_date: The date the card is scheduled for next review.
            current_interval_key: The current SRS interval key for this card.
            ease_history: A list storing the history of how easily the card was recalled.
        """
        self.card_id = card_id
        self.question = question
        self.answer = answer
        self.creation_date = creation_date or datetime.now()
        self.last_reviewed_date = last_reviewed_date
        self.next_review_date = next_review_date
        self.current_interval_key = current_interval_key
        self.ease_history = ease_history or []

    def __repr__(self):
        return (f"Flashcard(id='{self.card_id}', question='{self.question[:20]}...', "
                f"next_review='{self.next_review_date}')")

# Example (can be removed or moved to tests)
if __name__ == "__main__":
    card1 = Flashcard(card_id="1", question="What is Python?", answer="A programming language.")
    print(card1)

    card2 = Flashcard(card_id="2", question="What is SRS?", answer="Spaced Repetition System.",
                      current_interval_key="3_days",
                      next_review_date=datetime.now() + timedelta(days=3))
    print(card2)
    card2.ease_history.append("easy")
    print(card2.ease_history)

```
