from typing import Any, cast

from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import DBSession
from database.repositories.base import BaseRepository
from database.repositories.glossary_term import GlossaryTermRepository


class RepositoryManager:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._repositories: dict[str, BaseRepository[Any]] = {}

    @property
    def glossary_term(self) -> GlossaryTermRepository:
        if "glossary_term" not in self._repositories:
            self._repositories["glossary_term"] = GlossaryTermRepository(self._session)
        return cast(GlossaryTermRepository, self._repositories["glossary_term"])


async def get_repository_manager(session: DBSession) -> RepositoryManager:
    return RepositoryManager(session)
