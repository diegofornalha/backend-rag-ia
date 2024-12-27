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
    """Adiciona um novo documento e retorna informações detalhadas."""
    try:
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
        embedding = model.get_embedding(document.content)
        logger.info(f"✅ Embedding gerado: {len(embedding)} dimensões")
        
        # Prepara os dados para inserção
        data = {
            "content": document.content,
            "metadata": document.metadata,
            "embedding": embedding,
            "document_hash": document_hash
        }
        
        # Insere no Supabase
        logger.info("💾 Inserindo documento no Supabase...")
        response = supabase.table("documents").insert(data).execute()
        logger.info(f"✅ Documento inserido: {response.data[0]['id']}")
        
        # Atualiza a contagem
        logger.info("🔄 Atualizando contagem de documentos...")
        new_count = await update_documents_count()
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
    """Verifica o status da API e retorna informações detalhadas."""
    try:
        logger.info("🔍 Iniciando health check...")
        
        # Verifica conexão com Supabase
        if not supabase:
            logger.error("❌ Cliente Supabase não inicializado")
            raise RuntimeError("Cliente Supabase não inicializado")
            
        # Consulta documentos
        logger.info("📝 Consultando documentos...")
        docs = supabase.table("documents").select("id").execute()
        count = len(docs.data)
        logger.info(f"📊 Contagem bruta: {count}")
        
        # Atualiza a contagem na tabela de estatísticas
        logger.info("🔄 Atualizando contagem...")
        await update_documents_count()
        
        # Verifica embeddings
        logger.info("🔤 Consultando embeddings...")
        embeddings = supabase.table("embeddings").select("id").execute()
        embeddings_count = len(embeddings.data)
        logger.info(f"📊 Total de embeddings: {embeddings_count}")
        
        # Busca a contagem da tabela de estatísticas
        logger.info("📊 Buscando contagem armazenada...")
        stats = supabase.table("statistics").select("*").eq("key", "documents_count").execute()
        stored_count = stats.data[0]["value"] if stats.data else count
        logger.info(f"📊 Contagem armazenada: {stored_count}")
        
        result = {
            "status": "healthy",
            "message": "API está funcionando normalmente",
            "documents_count": stored_count,
            "embeddings_count": embeddings_count,
            "timestamp": datetime.now().isoformat(),
            "debug": {
                "raw_count": count,
                "stored_count": stored_count,
                "last_update": stats.data[0]["updated_at"] if stats.data else None
            }
        }
        logger.info(f"📤 Retornando resposta: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro no health check: {str(e)}")
        logger.exception("Detalhes do erro:")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "message": str(e),
                "documents_count": 0,
                "timestamp": datetime.now().isoformat()
            }
        )

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