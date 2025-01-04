from fastapi import FastAPI
from .routes import documents, cache

app = FastAPI(
    title="Backend RAG IA",
    version="1.0.0"
)

app.include_router(documents.router)
app.include_router(cache.router)

@app.get("/")
async def root():
    return {
        "name": "Backend RAG IA",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "online"
    } 