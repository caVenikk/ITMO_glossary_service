from logging import getLogger

from fastapi import FastAPI

from config import get_settings
from database.fixtures import FIXTURES_DIR
from database.fixtures.loader import FixtureLoader
from database.session import AsyncSessionLocal
from routes import glossary_router

logger = getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title="Glossary API",
    root_path="/api",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def load_initial_data() -> None:
    logger.info("Starting initial data load...")
    async with AsyncSessionLocal() as session:
        loader = FixtureLoader(session, "database.models", logger)
        results = await loader.load_all_fixtures(FIXTURES_DIR)
        if not all(results.values()):
            logger.warning("Some fixtures failed to load: %s", {k: v for k, v in results.items() if not v})
        else:
            logger.info("Initial data load completed successfully!")


app.include_router(glossary_router)
