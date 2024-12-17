from fastapi import HTTPException


class NotFound(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=404, detail=message)


class BadRequest(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)


class ValidationError(HTTPException):
    def __init__(self, errors: dict[str, list[str]]):
        super().__init__(status_code=400, detail=errors)
