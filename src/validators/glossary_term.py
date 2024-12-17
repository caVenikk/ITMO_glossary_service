from collections import defaultdict

from database.repositories.dependencies import CRUD
from exceptions.base import ValidationError
from schemas.glossary_term import GlossaryTermCreate, GlossaryTermUpdate


class BaseGlossaryTermValidator:
    glossary_term: GlossaryTermCreate | GlossaryTermUpdate

    def __init__(self, crud: CRUD):
        self.crud = crud
        self.errors: dict[str, list[str]] = defaultdict(list)

    async def validate(self) -> None:
        raise NotImplementedError("validate method must be implemented")

    async def validate_unique(self) -> None:
        existing = await self.crud.glossary_term.get_by_term(self.glossary_term.term)  # type: ignore[arg-type]
        if existing:
            self.errors["term"].append(f"Glossary term with term '{self.glossary_term.term}' already exists")

    def validate_definition(self) -> None:
        if len(self.glossary_term.definition) < 1:  # type: ignore[arg-type]
            self.errors["definition"].append("Definition is required")


class GlossaryTermCreateValidator(BaseGlossaryTermValidator):
    def __init__(self, glossary_term: GlossaryTermCreate, crud: CRUD):
        super().__init__(crud)
        self.glossary_term = glossary_term

    async def validate(self) -> None:
        await self.validate_unique()
        self.validate_definition()

        if self.errors:
            raise ValidationError(errors=self.errors)


class GlossaryTermUpdateValidator(BaseGlossaryTermValidator):
    def __init__(self, glossary_term: GlossaryTermUpdate, id: int, crud: CRUD):
        super().__init__(crud)
        self.glossary_term = glossary_term
        self.id = id

    async def validate(self) -> None:
        if self.glossary_term.term is not None:
            await self.validate_unique()
        if self.glossary_term.definition is not None:
            self.validate_definition()

        if self.errors:
            raise ValidationError(errors=self.errors)

    async def validate_unique(self) -> None:
        existing = await self.crud.glossary_term.get_by_term(self.glossary_term.term)  # type: ignore[arg-type]
        if existing and existing.id != self.id:
            self.errors["term"].append(f"Glossary term with term '{self.glossary_term.term}' already exists")
