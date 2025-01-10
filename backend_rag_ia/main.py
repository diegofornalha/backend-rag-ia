from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Backend RAG IA",
    description="Backend para o sistema RAG IA",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "Backend RAG IA API",
        "docs": "/docs"
    } 