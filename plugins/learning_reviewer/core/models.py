"""
Data models for long-term learning tracking.
"""
from datetime import datetime, date
from typing import Optional, Dict, Any, ClassVar
from pydantic import BaseModel, Field
import json


class LongTermParams(BaseModel):
    """Long-term memory parameters for a learning card."""
    longTermN: int = Field(default=0, ge=0, description="Cross-day consecutive correct count (0-6)")
    intervalDays: int = Field(default=1, ge=1, description="Current interval in days")
    ef: float = Field(default=2.5, ge=1.3, description="Easiness factor [1.3, ∞)")
    dueDate: str = Field(default="", description="Next review date (YYYY-MM-DD)")
    lastReviewed: str = Field(default="", description="Last review date (YYYY-MM-DD)")
    createdAt: str = Field(default="", description="Creation date (YYYY-MM-DD)")
    mastered: bool = Field(default=False, description="Long-term mastery status")

    # Base intervals for longTermN values 1-6
    BASE_INTERVALS: ClassVar[list[int]] = [1, 1, 3, 7, 15, 30]

    def update_interval_days(self) -> None:
        """Update intervalDays based on longTermN and EF factor."""
        if self.longTermN >= 7:
            self.mastered = True
            self.intervalDays = 0
            return

        if 1 <= self.longTermN <= 6:
            base_days = self.BASE_INTERVALS[self.longTermN - 1]
            self.intervalDays = round(base_days * (self.ef / 2.5))
        else:  # longTermN == 0
            self.intervalDays = 1

    def update_due_date(self, review_date: Optional[date] = None) -> None:
        """Update due date based on intervalDays."""
        if review_date is None:
            review_date = date.today()

        if self.intervalDays > 0:
            from datetime import timedelta
            due_date = review_date + timedelta(days=self.intervalDays)
            self.dueDate = due_date.isoformat()
        else:
            self.dueDate = ""

    def apply_correct_answer(self, review_date: Optional[date] = None) -> None:
        """Update parameters when card is answered correctly."""
        if review_date is None:
            review_date = date.today()

        # Increment longTermN only if first review of the day for this card
        # (This check should be done by the caller)
        self.longTermN += 1
        self.lastReviewed = review_date.isoformat()

        # Update interval and due date
        self.update_interval_days()
        self.update_due_date(review_date)

    def apply_wrong_answer(self, review_date: Optional[date] = None) -> None:
        """Update parameters when card is answered incorrectly."""
        if review_date is None:
            review_date = date.today()

        # Reset longTermN to 0
        self.longTermN = 0

        # Apply penalty to EF factor
        self.ef = max(self.ef - 0.2, 1.3)

        self.lastReviewed = review_date.isoformat()

        # Update interval and due date
        self.update_interval_days()
        self.update_due_date(review_date)

    def is_due(self, target_date: Optional[date] = None) -> bool:
        """Check if card is due for review on target_date."""
        if self.mastered:
            return False

        if target_date is None:
            target_date = date.today()

        if not self.dueDate:
            return True

        try:
            due_date = date.fromisoformat(self.dueDate)
            return due_date <= target_date
        except ValueError:
            return True

    @classmethod
    def create_new(cls, created_date: Optional[date] = None) -> 'LongTermParams':
        """Create new long-term parameters for a new card."""
        if created_date is None:
            created_date = date.today()

        params = cls(
            createdAt=created_date.isoformat(),
            lastReviewed=created_date.isoformat(),
        )
        params.update_due_date(created_date)
        return params


class Card(BaseModel):
    """Complete learning card with long-term parameters."""
    id: str
    question: str
    answer: str

    # Original fields (simplified)
    _reviewCount: int = 0
    _consecutiveCorrect: int = 0
    _learningStep: int = 0
    _mastered: bool = False  # Daily mastery status (original meaning)
    _wrongCount: int = 0
    _correctCount: int = 0

    # Long-term parameters
    longTermParams: LongTermParams = Field(default_factory=LongTermParams)

    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary for JSON serialization."""
        data = self.dict(exclude={'longTermParams'})
        data.update(self.longTermParams.dict())
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Card':
        """Create card from dictionary."""
        # Extract long-term parameters
        lt_keys = LongTermParams.__fields__.keys()
        lt_data = {k: data.pop(k) for k in list(data.keys()) if k in lt_keys}

        # Create long-term params
        long_term_params = LongTermParams(**lt_data) if lt_data else LongTermParams()

        # Create card
        return cls(**data, longTermParams=long_term_params)