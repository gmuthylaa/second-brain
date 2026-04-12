from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import shared  # noqa: F401 - ensure package import
from . import ingest as ingest_module
from . import search as search_module
from . import summaries as summaries_module
from . import chat as chat_module
from . import ingest_review as ingest_review_module
from .settings import get_settings
from . import shared

settings = get_settings()


app = FastAPI(title="Second Brain API")

# CORS so React can talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from api package
app.include_router(ingest_module.router)
app.include_router(search_module.router)
app.include_router(summaries_module.router)
app.include_router(chat_module.router)
app.include_router(ingest_review_module.router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "docs_count": shared.vectorstore._collection.count()}
