from collections.abc import Sequence
from typing import Any, Generic

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.types import ModelType


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: int) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[ModelType]:
        stmt = select(self.model)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, **kwargs: Any) -> ModelType:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: int, **kwargs: Any) -> ModelType | None:
        obj = await self.get(id)
        if obj:
            for key, value in kwargs.items():
                if hasattr(obj, key) and key not in ["id", "created_at", "updated_at"] and value is not None:
                    setattr(obj, key, value)
            await self.session.commit()
            await self.session.refresh(obj)
        return obj

    async def delete(self, id: int) -> ModelType | None:
        obj = await self.get(id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
            return obj
        return None
