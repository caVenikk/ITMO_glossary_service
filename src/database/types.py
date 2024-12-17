from typing import TypeVar

from database.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
