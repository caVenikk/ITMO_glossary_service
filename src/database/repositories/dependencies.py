from typing import Annotated

from fastapi import Depends

from database.repositories.manager import RepositoryManager, get_repository_manager

CRUD = Annotated[RepositoryManager, Depends(get_repository_manager)]
