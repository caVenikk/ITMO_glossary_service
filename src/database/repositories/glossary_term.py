from typing import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import GlossaryTerm

from .base import BaseRepository


class GlossaryTermRepository(BaseRepository[GlossaryTerm]):
    def __init__(self, session: AsyncSession):
        super().__init__(GlossaryTerm, session)

    async def get_by_term(self, query: str) -> GlossaryTerm | None:
        stmt = select(GlossaryTerm).where(GlossaryTerm.term == query)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_count(self, search_query: str | None = None) -> int:
        stmt = select(func.count()).select_from(GlossaryTerm)
        if search_query:
            stmt = stmt.where(
                or_(
                    GlossaryTerm.term.ilike(f"%{search_query}%"),
                    GlossaryTerm.definition.ilike(f"%{search_query}%"),
                ),
            )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def search(
        self,
        query: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[GlossaryTerm]:
        stmt = select(GlossaryTerm).where(
            or_(
                GlossaryTerm.term.ilike(f"%{query}%"),
                GlossaryTerm.definition.ilike(f"%{query}%"),
            ),
        )
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()
