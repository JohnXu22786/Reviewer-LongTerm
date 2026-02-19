"""
Default configuration values for Learning Reviewer Plugin.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class DefaultConfig:
    """Default configuration values."""
    # Data directory
    DATA_DIR: str = "./data"

    # Debug mode
    DEBUG_MODE: bool = False

    # Default review limit
    DEFAULT_REVIEW_LIMIT: int = 20

    # Base intervals for long-term memory (days)
    BASE_INTERVALS: List[int] = (1, 1, 3, 7, 15, 30)

    # EF factor settings
    INITIAL_EF: float = 2.5
    MIN_EF: float = 1.3
    EF_PENALTY: float = 0.2

    # Mastery threshold (longTermN >= MASTERY_THRESHOLD)
    MASTERY_THRESHOLD: int = 7


# Default configuration instance
default_config = DefaultConfig()