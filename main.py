from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import sys
import fastapi

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carrega configurações
from config.config import get_settings
settings = get_settings()

# Importa modelos e serviços do cluster Supabase
from clusters_API.API_supabase.models.database import Document, Query
from clusters_API.API_supabase.services.supabase_client import create_supabase_client

# Importa routers dos diferentes clusters
from clusters_API.API_supabase.api import router as supabase_router
from clusters_API.API_whatsapp.api import router as whatsapp_router
from clusters_API.API_tools.api import router as tools_router

# Configuração do Supabase
try:
    supabase = create_supabase_client()
    logger.info("✅ Cliente Supabase inicializado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar cliente Supabase: {str(e)}")
    if settings.ENVIRONMENT == "production":
        raise
    else:
        logger.warning("⚠️ Continuando sem Supabase em ambiente de desenvolvimento")
        supabase = None

# Carrega o modelo
try:
    model = SentenceTransformer(settings.MODEL_NAME)
    logger.info(f"✅ Modelo {settings.MODEL_NAME} carregado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao carregar modelo: {str(e)}")
    raise

# Inicializa o cluster
from clusters_API import get_cluster
cluster = get_cluster()
logger.info(f"✅ Cluster inicializado: {cluster.__class__.__name__}")

# Cria a aplicação FastAPI
app = FastAPI(
    title="API RAG",
    description="""
    Sistema RAG (Retrieval-Augmented Generation) que integra:

    ### API Supabase
    Gerenciamento de documentos e embeddings para recuperação de informações
    
    ### API WhatsApp
    Integração com WhatsApp para comunicação e respostas
    
    ### API Tools
    Ferramentas e utilitários de suporte ao sistema RAG
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Adiciona middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os routers dos diferentes clusters
app.include_router(supabase_router, prefix="/api/v1/rag/supabase", tags=["RAG Supabase"])
app.include_router(whatsapp_router, prefix="/api/v1/rag/whatsapp", tags=["RAG WhatsApp"])
app.include_router(tools_router, prefix="/api/v1/rag/tools", tags=["RAG Tools"])

# Middleware de logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    method = request.method
    path = request.url.path
    
    logger.info(f"📥 {method} {path} - Iniciando requisição")
    
    try:
        response = await call_next(request)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"📤 {method} {path} - {response.status_code} - {duration:.2f}s")
        
        return response
    except Exception as e:
        logger.error(f"❌ {method} {path} - Erro: {str(e)}")
        raise

# Middleware de resposta JSON
@app.middleware("http")
async def add_json_headers(request: Request, call_next):
    response = await call_next(request)
    if response.headers.get("content-type") == "application/json":
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Expose-Headers"] = "*"
    return response

# Handler de erros global
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.get("/api/v1/health")
async def health_check():
    """Verifica a saúde da API."""
    try:
        health = await cluster.get_health_check()
        return {
            "status": "healthy",
            "message": "API está funcionando normalmente",
            "details": health,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar saúde da API: {str(e)}"
        )

@app.get("/api/v1/documents/check/{document_hash}")
async def check_document(document_hash: str):
    """Verifica se um documento já existe baseado no hash."""
    try:
        if not supabase:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "message": "Supabase não está disponível"
                }
            )
            
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
    """Adiciona um novo documento e retorna informações detalhadas."""
    try:
        if not supabase:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "message": "Supabase não está disponível"
                }
            )
            
        logger.info("📝 Iniciando adição de documento...")
        
        # Extrai o document_hash dos metadados
        document_hash = document.metadata.pop("document_hash", None)
        logger.info(f"🔑 Hash do documento: {document_hash}")
        
        # Verifica se já existe um documento com este hash
        if document_hash:
            logger.info("🔍 Verificando documento existente...")
            existing = supabase.table("documents").select("id").eq("document_hash", document_hash).execute()
            if len(existing.data) > 0:
                logger.info(f"⚠️ Documento já existe: {existing.data[0]['id']}")
                return JSONResponse(
                    status_code=409,
                    content={
                        "status": "error",
                        "message": "Documento já existe",
                        "document_id": existing.data[0]["id"]
                    }
                )
        
        # Gera o embedding
        logger.info("🔤 Gerando embedding...")
        embedding = model.encode(document.content)
        logger.info(f"✅ Embedding gerado: {len(embedding)} dimensões")
        
        # Prepara os dados para inserção
        data = {
            "content": document.content,
            "metadata": document.metadata,
            "embedding": embedding.tolist(),
            "document_hash": document_hash,
            "created_at": datetime.now().isoformat()
        }
        
        # Insere no Supabase
        logger.info("💾 Inserindo documento no Supabase...")
        response = supabase.table("documents").insert(data).execute()
        logger.info(f"✅ Documento inserido: {response.data[0]['id']}")
        
        # Atualiza a contagem
        logger.info("🔄 Atualizando contagem de documentos...")
        new_count = await cluster.update_documents_count()
        logger.info(f"📊 Nova contagem: {new_count}")
        
        # Retorna resposta detalhada
        result = {
            "status": "success",
            "message": "Documento adicionado com sucesso",
            "document": response.data[0],
            "documents_count": new_count
        }
        logger.info(f"📤 Retornando resposta: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar documento: {str(e)}")
        logger.exception("Detalhes do erro:")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "detail": "Erro ao adicionar documento"
            }
        )

@app.post("/api/v1/search/")
async def search_documents(query: Query):
    """Busca documentos similares baseado em uma query."""
    try:
        # Define um valor padrão para k se for None
        k = query.k if query.k is not None else 4
        results = await cluster.search_similar(query.query, k)
        return {
            "status": "success",
            "results": results,
            "count": len(results),
            "query": query.query
        }
    except Exception as e:
        logger.error(f"Erro na busca: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao realizar busca: {str(e)}"
        )

@app.delete("/api/v1/documents/{document_id}")
async def delete_document(document_id: str):
    """Remove um documento e seus embeddings."""
    try:
        if not supabase:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "message": "Supabase não está disponível"
                }
            )
            
        # Remove embeddings
        success = await cluster.delete_embeddings(document_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Erro ao remover embeddings"
            )
            
        # Remove documento
        response = supabase.table("documents").delete().eq("id", document_id).execute()
        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Documento não encontrado"
            )
            
        return {
            "status": "success",
            "message": "Documento removido com sucesso",
            "document_id": document_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover documento: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao remover documento: {str(e)}"
        )

@app.delete("/api/v1/documents-all")
async def delete_all_documents():
    """Remove todos os documentos e embeddings."""
    try:
        if not supabase:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "message": "Supabase não está disponível"
                }
            )
            
        # Remove todos os documentos
        response = supabase.table("documents").delete().neq("id", "").execute()
        
        # Remove todos os embeddings
        response_emb = supabase.table("embeddings").delete().neq("id", "").execute()
        
        return {
            "status": "success",
            "message": "Todos os documentos foram removidos",
            "documents_removed": len(response.data),
            "embeddings_removed": len(response_emb.data)
        }
    except Exception as e:
        logger.error(f"Erro ao remover todos os documentos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao remover documentos: {str(e)}"
        )

@app.get("/api/v1/debug")
async def debug_info():
    """Retorna informações de debug."""
    try:
        return {
            "status": "success",
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "model": {
                "name": settings.MODEL_NAME,
                "embedding_dim": settings.EMBEDDING_DIM
            },
            "supabase": {
                "available": supabase is not None,
                "url": settings.SUPABASE_URL if settings.DEBUG else "***",
            },
            "cluster": {
                "type": cluster.__class__.__name__,
                "documents": await cluster.get_documents_count(),
                "embeddings": await cluster.get_embeddings_count()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter informações de debug: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter informações de debug: {str(e)}"
        ) 