from pydantic import BaseModel


class GlossaryTermBase(BaseModel):
    term: str
    definition: str


class GlossaryTerm(GlossaryTermBase):
    id: int

    class Config:
        from_attributes = True


class GlossaryTermCreate(GlossaryTermBase):
    pass


class GlossaryTermUpdate(BaseModel):
    term: str | None = None
    definition: str | None = None
