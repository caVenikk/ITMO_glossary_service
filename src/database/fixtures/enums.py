from enum import Enum


class FixtureLoadStatus(str, Enum):
    """Enum for fixture load status"""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"
