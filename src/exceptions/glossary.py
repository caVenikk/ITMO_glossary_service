from .base import BadRequest, NotFound


class GlossaryTermNotFound(NotFound):
    def __init__(self, id: int):
        super().__init__(f"Glossary term with id {id} not found")


class GlossaryTermAlreadyExists(BadRequest):
    def __init__(self, term: str):
        super().__init__(f"Glossary term '{term}' already exists")
