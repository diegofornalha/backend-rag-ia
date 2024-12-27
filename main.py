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
app = FastAPI()

# Adiciona middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        # Gera o embedding
        embedding = model.get_embedding(document.content)
        
        # Prepara os dados para inserção
        data = {
            "content": document.content,
            "metadata": document.metadata,  # Metadata sem o hash
            "embedding": embedding,
            "document_hash": document_hash  # Hash no nível raiz
        }
        
        # Insere no Supabase
        response = supabase.table("documents").insert(data).execute()
        
        return response.data[0]
        
    except Exception as e:
        logger.error(f"Erro ao adicionar documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

# Constantes e configurações
ALLOW_EMPTY_DEPLOYS = False  # Nova constante para controlar deploys vazios

async def update_documents_count():
    """Atualiza a contagem de documentos na tabela de estatísticas."""
    try:
        # Consulta a quantidade atual de documentos
        docs = supabase.table("documents").select("id").execute()
        count = len(docs.data)
        
        # Atualiza ou insere a contagem na tabela de estatísticas
        stats = {
            "key": "documents_count",
            "value": count,
            "updated_at": datetime.now().isoformat()
        }
        
        # Tenta atualizar primeiro
        response = supabase.table("statistics").upsert(stats).execute()
        
        logger.info(f"✅ Contagem de documentos atualizada: {count}")
        return count
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar contagem de documentos: {str(e)}")
        return None

@app.get("/api/v1/health")
async def health_check():
    """Verifica o status da API e retorna a contagem de documentos."""
    try:
        logger.info("🔍 Iniciando health check...")
        debug_info = {
            "model_status": "not_checked",
            "supabase_status": "not_checked",
            "database_status": "not_checked"
        }
        
        # Verifica modelo
        try:
            if not model:
                debug_info["model_status"] = "not_initialized"
                raise RuntimeError("Modelo não inicializado")
            test_embedding = model.get_embedding("teste")
            if len(test_embedding) > 0:
                debug_info["model_status"] = "ok"
                debug_info["embedding_size"] = len(test_embedding)
        except Exception as e:
            debug_info["model_status"] = "error"
            debug_info["model_error"] = str(e)
            logger.error(f"❌ Erro ao verificar modelo: {str(e)}")
        
        # Verifica conexão com Supabase
        if not supabase:
            debug_info["supabase_status"] = "not_initialized"
            logger.error("❌ Cliente Supabase não inicializado")
            raise RuntimeError("Cliente Supabase não inicializado")
        else:
            debug_info["supabase_status"] = "initialized"
            
        # Testa conexão com banco
        try:
            test_query = supabase.table("documents").select("count").execute()
            debug_info["database_status"] = "ok"
        except Exception as e:
            debug_info["database_status"] = "error"
            debug_info["database_error"] = str(e)
            logger.error(f"❌ Erro ao testar conexão com banco: {str(e)}")
            
        # Consulta documentos
        logger.info("📝 Consultando documentos...")
        try:
            docs = supabase.table("documents").select("*").execute()
            count = len(docs.data)
            debug_info["documents_query"] = "ok"
            debug_info["documents_raw_count"] = count
            logger.info(f"📊 Total de documentos: {count}")
        except Exception as e:
            debug_info["documents_query_error"] = str(e)
            count = 0
        
        # Atualiza a contagem na tabela de estatísticas
        try:
            stats_count = await update_documents_count()
            debug_info["stats_update"] = "ok"
            debug_info["stats_count"] = stats_count
        except Exception as e:
            debug_info["stats_update_error"] = str(e)
        
        # Verifica embeddings
        logger.info("🔤 Consultando embeddings...")
        try:
            embeddings = supabase.table("embeddings").select("*").execute()
            embeddings_count = len(embeddings.data)
            debug_info["embeddings_query"] = "ok"
            debug_info["embeddings_count"] = embeddings_count
            logger.info(f"📊 Total de embeddings: {embeddings_count}")
        except Exception as e:
            debug_info["embeddings_query_error"] = str(e)
            embeddings_count = 0
        
        # Busca a contagem da tabela de estatísticas
        try:
            stats = supabase.table("statistics").select("*").eq("key", "documents_count").execute()
            stored_count = stats.data[0]["value"] if stats.data else count
            debug_info["stats_query"] = "ok"
            debug_info["stored_count"] = stored_count
        except Exception as e:
            debug_info["stats_query_error"] = str(e)
            stored_count = count
        
        logger.info(f"✅ Health check completo - Documentos: {count}, Embeddings: {embeddings_count}, Contagem armazenada: {stored_count}")
        
        return {
            "status": "healthy",
            "message": "API está funcionando normalmente",
            "documents_count": stored_count,
            "embeddings_count": embeddings_count,
            "timestamp": datetime.now().isoformat(),
            "documents": docs.data if "docs" in locals() else [],
            "allow_empty_deploys": ALLOW_EMPTY_DEPLOYS,
            "debug_info": debug_info
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no health check: {str(e)}")
        logger.exception("Detalhes do erro:")
        return {
            "status": "unhealthy",
            "message": str(e),
            "documents_count": 0,
            "timestamp": datetime.now().isoformat(),
            "debug_info": {"error": str(e)}
        } 

@app.post("/api/v1/search/")
async def search_documents(query: Query):
    """Realiza busca semântica nos documentos."""
    try:
        # Verifica se é uma pergunta sobre quantidade de documentos
        if any(keyword in query.query.lower() for keyword in ["quantos documentos", "número de documentos", "total de documentos"]):
            response = supabase.table("documents").select("id").execute()
            count = len(response.data)
            return [{
                "content": f"Atualmente há {count} documento(s) no sistema.",
                "metadata": {"type": "system_info"}
            }]
            
        # Busca semântica normal
        query_embedding = model.get_embedding(query.query)
        
        # Realiza a busca
        results = supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.7,
                'match_count': query.k or 4
            }
        ).execute()
        
        return results.data
        
    except Exception as e:
        logger.error(f"Erro na busca: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.delete("/api/v1/documents/{document_id}")
async def delete_document(document_id: int):
    """Remove um documento pelo ID."""
    try:
        # Remove o documento
        response = supabase.table("documents").delete().eq("id", document_id).execute()
        
        if len(response.data) > 0:
            return {"message": f"Documento {document_id} removido com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
            
    except Exception as e:
        logger.error(f"Erro ao remover documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/documents-all")
async def delete_all_documents():
    """Remove todos os documentos."""
    try:
        # Remove todos os documentos
        response = supabase.table("documents").delete().neq("id", 0).execute()
        count = len(response.data)
        
        return {
            "message": f"{count} documento(s) removido(s) com sucesso",
            "count": count
        }
            
    except Exception as e:
        logger.error(f"Erro ao remover documentos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 