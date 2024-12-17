from typing import Any

from .enums import FixtureLoadStatus


class FixtureResult:
    """Class to hold fixture loading results"""

    def __init__(self, fixture_name: str):
        self.fixture_name = fixture_name
        self.status = FixtureLoadStatus.SUCCESS
        self.created = 0
        self.updated = 0
        self.failed = 0
        self.errors: list[str] = []

    @property
    def is_successful(self) -> bool:
        return self.status == FixtureLoadStatus.SUCCESS

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture": self.fixture_name,
            "status": self.status,
            "stats": {
                "created": self.created,
                "updated": self.updated,
                "failed": self.failed,
            },
            "errors": self.errors,
        }
