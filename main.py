from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
import sys
from models.document import Document

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

# Carrega o modelo
model = SentenceTransformer('all-MiniLM-L6-v2')

# Cria a aplicação FastAPI
app = FastAPI(
    title="Documents API",
    description="API para processamento de documentos e embeddings",
    version="1.0.0"
)

# Configuração CORS específica para porta 3000
origins = [
    "http://localhost:3000",  # Frontend na porta 3000
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Métodos HTTP permitidos
    allow_headers=["*"],
)

# Middleware de logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    method = request.method
    path = request.url.path
    
    response = await call_next(request)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() * 1000
    
    logger.info(f"{method} {path} - {response.status_code} - {duration:.2f}ms")
    
    return response

@app.get("/api/v1/documents/check/{document_hash}")
async def check_document(document_hash: str):
    """Verifica se um documento já existe baseado no hash."""
    try:
        # Consulta o Supabase
        response = supabase.table("documents").select("id").eq("document_hash", document_hash).execute()
        
        # Se encontrou algum documento, retorna 200
        if len(response.data) > 0:
            return {"exists": True, "message": "Documento já existe"}
        
        # Se não encontrou, retorna 404
        return JSONResponse(
            status_code=404,
            content={"exists": False, "message": "Documento não encontrado"}
        )
    except Exception as e:
        logger.error(f"Erro ao verificar documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.post("/api/v1/documents/")
async def add_document(document: Document):
    """Adiciona um novo documento e gera seu embedding."""
    try:
        # Extrai o document_hash dos metadados
        document_hash = document.metadata.pop("document_hash", None)  # Remove do metadata e guarda
        
        # Verifica se já existe um documento com este hash
        if document_hash:
            existing = supabase.table("documents").select("id").eq("document_hash", document_hash).execute()
            if len(existing.data) > 0:
                return JSONResponse(
                    status_code=409,  # Conflict
                    content={"message": "Documento já existe"}
                )
        
        # Primeiro, insere o documento
        doc_data = {
            "content": document.content,
            "metadata": document.metadata,  # Metadata sem o hash
            "document_hash": document_hash  # Hash no nível raiz
        }
        
        doc_response = supabase.table("documents").insert(doc_data).execute()
        document_id = doc_response.data[0]["id"]
        
        # Gera o embedding
        embedding = model.encode(document.content)
        
        # Insere o embedding
        embedding_data = {
            "document_id": document_id,
            "embedding": embedding.tolist()  # Convertendo numpy array para lista
        }
        
        embedding_response = supabase.table("embeddings").insert(embedding_data).execute()
        
        # Atualiza o documento com o ID do embedding
        supabase.table("documents").update({"embedding_id": embedding_response.data[0]["id"]}).eq("id", document_id).execute()
        
        return doc_response.data[0]
        
    except Exception as e:
        logger.error(f"Erro ao adicionar documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/api/v1/health")
async def health_check():
    """Verifica o status da API."""
    try:
        # Conta documentos
        result = supabase.table("documents").select("id", count="exact").execute()
        count = result.count if result.count is not None else 0
        
        return {
            "status": "healthy",
            "message": "API está funcionando normalmente",
            "documents_count": count
        }
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e)
        } 