import uvicorn

from config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
