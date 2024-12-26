from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from services.vector_store import VectorStore
from models.load_knowledge_base import load_knowledge_base

app = FastAPI()

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização do VectorStore
vector_store = VectorStore()

# Carrega documentos iniciais se necessário
if len(vector_store.documents) == 0:
    load_knowledge_base(vector_store)

# Inclui as rotas da API
app.include_router(router, prefix="/api/v1") 