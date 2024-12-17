from fastapi import APIRouter, Query
from pydantic import TypeAdapter

from database.repositories.dependencies import CRUD
from exceptions.glossary import GlossaryTermNotFound
from schemas.common import PaginatedResponse, paginate
from schemas.glossary_term import GlossaryTerm, GlossaryTermCreate, GlossaryTermUpdate
from validators.glossary_term import GlossaryTermCreateValidator, GlossaryTermUpdateValidator

router = APIRouter(prefix="/glossary")


@router.get("/", response_model=PaginatedResponse[GlossaryTerm])
async def get_glossary_terms(
    crud: CRUD,
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse[GlossaryTerm]:
    result = await crud.glossary_term.get_all(limit, offset)
    return paginate(
        TypeAdapter(list[GlossaryTerm]).validate_python(result),
        await crud.glossary_term.get_count(),
        limit,
    )


@router.get("/search")
async def search_glossary_terms(
    query: str,
    crud: CRUD,
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse[GlossaryTerm]:
    result = await crud.glossary_term.search(query, limit, offset)
    return paginate(
        TypeAdapter(list[GlossaryTerm]).validate_python(result),
        await crud.glossary_term.get_count(query),
        limit,
    )


@router.get("/{id}")
async def get_glossary_term(
    crud: CRUD,
    id: int,
) -> GlossaryTerm:
    result = await crud.glossary_term.get(id)
    if not result:
        raise GlossaryTermNotFound(id)
    return TypeAdapter(GlossaryTerm).validate_python(result)


@router.post("/")
async def create_glossary_term(
    crud: CRUD,
    glossary_term: GlossaryTermCreate,
) -> GlossaryTerm:
    validator = GlossaryTermCreateValidator(glossary_term, crud)
    await validator.validate()

    result = await crud.glossary_term.create(**glossary_term.model_dump())
    return TypeAdapter(GlossaryTerm).validate_python(result)


@router.put("/{id}")
async def update_glossary_term(
    crud: CRUD,
    id: int,
    glossary_term: GlossaryTermUpdate,
) -> GlossaryTerm:
    existing = await crud.glossary_term.get(id)
    if not existing:
        raise GlossaryTermNotFound(id)

    validator = GlossaryTermUpdateValidator(glossary_term, id, crud)
    await validator.validate()

    result = await crud.glossary_term.update(id, **glossary_term.model_dump())
    return TypeAdapter(GlossaryTerm).validate_python(result)


@router.delete("/{id}")
async def delete_glossary_term(
    crud: CRUD,
    id: int,
) -> GlossaryTerm:
    result = await crud.glossary_term.delete(id)
    if not result:
        raise GlossaryTermNotFound(id)
    return TypeAdapter(GlossaryTerm).validate_python(result)
