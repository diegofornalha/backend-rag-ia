"""Módulo principal da aplicação.

<<<<<<< Updated upstream
Este módulo contém as rotas e a lógica principal da API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_supabase_client
from .schemas import DocumentCreate, DocumentResponse, DocumentUpdate

# Constantes de tabelas
TABELA_BASE_CONHECIMENTO = 'rag.01_base_conhecimento_regras_geral'
TABELA_EMBEDDINGS = 'rag.02_embeddings_regras_geral'

app = FastAPI()
=======
Este módulo implementa os endpoints principais da API FastAPI,
incluindo gerenciamento de documentos, embeddings e operações em lote.
"""

import hashlib
import json
from datetime import datetime
from typing import Optional

import httpx
from fastapi import BackgroundTasks, Body, FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_supabase_client
from .schemas import (
    BatchOperation,
    Document,
    DocumentCreate,
    DocumentUpdate,
    Embedding,
    EmbeddingCreate,
    HealthCheck,
    LogEntry,
    Statistics,
)

# Configuração da API
app = FastAPI(
    title="CoFlow RAG API",
    description="API para gerenciamento de documentos e embeddings do sistema RAG",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)
>>>>>>> Stashed changes

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< Updated upstream
@app.post("/documents/", response_model=DocumentResponse)
async def create_document(document: DocumentCreate):
    """Cria um novo documento na base de conhecimento.
=======
# Cliente Supabase
supabase = get_supabase_client()

# Registrar tempo de início para health check
app.state.start_time = datetime.utcnow()

@app.post("/api/v1/documents", response_model=Document, tags=["Documentos"])
async def create_document(document: DocumentCreate) -> Document:
    """Cria um novo documento.
>>>>>>> Stashed changes

    Parameters
    ----------
    document : DocumentCreate
        Dados do documento a ser criado.

    Returns
    -------
<<<<<<< Updated upstream
    DocumentResponse
=======
    Document
>>>>>>> Stashed changes
        Documento criado.

    Raises
    ------
    HTTPException
<<<<<<< Updated upstream
        Se houver erro na criação ou documento duplicado.

    """
    try:
        supabase = get_supabase_client()
        content_hash = document.generate_hash()

        # Verificar duplicidade
        result = await (
            supabase.rpc('check_duplicate_content', {'content_hash': content_hash})
            .execute()
        )
        
=======
        Se houver erro ao criar o documento.
    """
    try:
        # Gerar hash do conteúdo
        content = json.dumps(document.conteudo, sort_keys=True)
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Verificar duplicidade
        result = await supabase.rpc('check_duplicate_content', {'content_hash': content_hash}).execute()
>>>>>>> Stashed changes
        if result.data:
            raise HTTPException(status_code=409, detail="Documento duplicado")

        # Preparar dados
        doc_data = {
            'titulo': document.titulo,
            'conteudo': document.conteudo,
            'content_hash': content_hash,
            'metadata': document.metadata or {}
        }

        # Inserir no Supabase
<<<<<<< Updated upstream
        result = await (
            supabase.table(TABELA_BASE_CONHECIMENTO)
            .insert(doc_data)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Erro ao criar documento"
            )

        return DocumentResponse(**result.data[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
=======
        result = await supabase.table('rag.01_base_conhecimento_regras_geral').insert(doc_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Erro ao criar documento")

        # Registrar no changelog
        await supabase.rpc(
            'log_change',
            {
                'operation': 'CREATE',
                'table_name': 'rag.01_base_conhecimento_regras_geral',
                'record_id': str(result.data[0]['id']),
                'new_data': doc_data
            }
        ).execute()

        return Document(**result.data[0])

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

@app.get("/api/v1/documents/{document_id}", response_model=Document, tags=["Documentos"])
async def get_document(document_id: str = Path(...)) -> Document:
>>>>>>> Stashed changes
    """Busca um documento por ID.

    Parameters
    ----------
    document_id : str
<<<<<<< Updated upstream
        ID do documento a ser buscado.

    Returns
    -------
    DocumentResponse
=======
        ID do documento.

    Returns
    -------
    Document
>>>>>>> Stashed changes
        Documento encontrado.

    Raises
    ------
    HTTPException
        Se o documento não for encontrado.
<<<<<<< Updated upstream

    """
    try:
        supabase = get_supabase_client()

        # Buscar documento
        result = await (
            supabase.table(TABELA_BASE_CONHECIMENTO)
            .select('*')
            .eq('id', document_id)
            .execute()
        )
=======
    """
    try:
        # Buscar documento
        result = await supabase.table('rag.01_base_conhecimento_regras_geral').select('*').eq('id', document_id).execute()
>>>>>>> Stashed changes

        if not result.data:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Buscar embedding associado
<<<<<<< Updated upstream
        embedding = await (
            supabase.table(TABELA_EMBEDDINGS)
            .select('*')
            .eq('document_id', document_id)
            .execute()
        )
=======
        embedding = await supabase.table('rag.02_embeddings_regras_geral').select('*').eq('document_id', document_id).execute()
>>>>>>> Stashed changes

        # Adicionar status do embedding aos metadados
        doc = result.data[0]
        doc['metadata'] = doc.get('metadata', {})
        doc['metadata']['has_embedding'] = bool(embedding.data)

<<<<<<< Updated upstream
        return DocumentResponse(**doc)

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err

@app.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(document_id: str, document: DocumentUpdate):
    """Atualiza um documento existente.
=======
        return Document(**doc)

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

@app.put("/api/v1/documents/{document_id}", response_model=Document, tags=["Documentos"])
async def update_document(
    document_id: str = Path(...),
    document: DocumentUpdate = Body(...)
) -> Document:
    """Atualiza um documento.
>>>>>>> Stashed changes

    Parameters
    ----------
    document_id : str
<<<<<<< Updated upstream
        ID do documento a ser atualizado.
    document : DocumentUpdate
        Dados para atualização do documento.

    Returns
    -------
    DocumentResponse
=======
        ID do documento.
    document : DocumentUpdate
        Dados para atualização.

    Returns
    -------
    Document
>>>>>>> Stashed changes
        Documento atualizado.

    Raises
    ------
    HTTPException
        Se o documento não for encontrado ou houver erro na atualização.
<<<<<<< Updated upstream

    """
    try:
        supabase = get_supabase_client()

        # Verificar se documento existe
        existing = await (
            supabase.table(TABELA_BASE_CONHECIMENTO)
            .select('*')
            .eq('id', document_id)
            .execute()
        )
=======
    """
    try:
        # Verificar se documento existe
        existing = await supabase.table('rag.01_base_conhecimento_regras_geral').select('*').eq('id', document_id).execute()
>>>>>>> Stashed changes

        if not existing.data:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Preparar dados para atualização
        update_data = document.dict(exclude_unset=True)

        if 'conteudo' in update_data:
            # Gerar novo hash se conteúdo foi atualizado
<<<<<<< Updated upstream
            content_hash = document.generate_hash()
            update_data['content_hash'] = content_hash

        # Atualizar documento
        result = await (
            supabase.table(TABELA_BASE_CONHECIMENTO)
            .update(update_data)
            .eq('id', document_id)
            .execute()
        )
=======
            content = json.dumps(update_data['conteudo'], sort_keys=True)
            update_data['content_hash'] = hashlib.sha256(content.encode()).hexdigest()

        # Atualizar documento
        result = await supabase.table('rag.01_base_conhecimento_regras_geral').update(update_data).eq('id', document_id).execute()
>>>>>>> Stashed changes

        if not result.data:
            raise HTTPException(status_code=500, detail="Erro ao atualizar documento")

<<<<<<< Updated upstream
        return DocumentResponse(**result.data[0])

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Remove um documento existente.
=======
        # Registrar no changelog
        await supabase.rpc(
            'log_change',
            {
                'operation': 'UPDATE',
                'table_name': 'rag.01_base_conhecimento_regras_geral',
                'record_id': document_id,
                'old_data': existing.data[0],
                'new_data': result.data[0]
            }
        ).execute()

        return Document(**result.data[0])

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

@app.delete("/api/v1/documents/{document_id}", tags=["Documentos"])
async def delete_document(document_id: str = Path(...)) -> dict:
    """Remove um documento.
>>>>>>> Stashed changes

    Parameters
    ----------
    document_id : str
<<<<<<< Updated upstream
        ID do documento a ser removido.
=======
        ID do documento.
>>>>>>> Stashed changes

    Returns
    -------
    dict
        Mensagem de confirmação.

    Raises
    ------
    HTTPException
        Se o documento não for encontrado ou houver erro na remoção.
<<<<<<< Updated upstream

    """
    try:
        supabase = get_supabase_client()

        # Verificar se documento existe
        existing = await (
            supabase.table(TABELA_BASE_CONHECIMENTO)
            .select('*')
            .eq('id', document_id)
            .execute()
        )
=======
    """
    try:
        # Verificar se documento existe
        existing = await supabase.table('rag.01_base_conhecimento_regras_geral').select('*').eq('id', document_id).execute()
>>>>>>> Stashed changes

        if not existing.data:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Remover embedding primeiro (se existir)
<<<<<<< Updated upstream
        await (
            supabase.table(TABELA_EMBEDDINGS)
            .delete()
            .eq('document_id', document_id)
            .execute()
        )

        # Remover documento
        result = await (
            supabase.table(TABELA_BASE_CONHECIMENTO)
            .delete()
            .eq('id', document_id)
            .execute()
        )
=======
        await supabase.table('rag.02_embeddings_regras_geral').delete().eq('document_id', document_id).execute()

        # Remover documento
        result = await supabase.table('rag.01_base_conhecimento_regras_geral').delete().eq('id', document_id).execute()
>>>>>>> Stashed changes

        if not result.data:
            raise HTTPException(status_code=500, detail="Erro ao remover documento")

<<<<<<< Updated upstream
        return {"message": "Documento removido com sucesso"}

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err
=======
        # Registrar no changelog
        await supabase.rpc(
            'log_change',
            {
                'operation': 'DELETE',
                'table_name': 'rag.01_base_conhecimento_regras_geral',
                'record_id': document_id,
                'old_data': existing.data[0]
            }
        ).execute()

        # Atualizar estatísticas
        await supabase.rpc('update_statistics').execute()

        return {"message": "Documento removido com sucesso"}

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

@app.post("/api/v1/embeddings", response_model=list[float], tags=["Embeddings"])
async def generate_embedding(data: EmbeddingCreate) -> list[float]:
    """Gera embedding para um texto.

    Parameters
    ----------
    data : EmbeddingCreate
        Texto para gerar embedding.

    Returns
    -------
    list[float]
        Vetor de embedding gerado.

    Raises
    ------
    HTTPException
        Se houver erro ao gerar o embedding.
    """
    try:
        # Chamar API do CoFlow para gerar embedding
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.coflow.com.br/api/v1/embeddings',
                json={'text': data.text}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Erro ao gerar embedding")

            return response.json()['embedding']

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

@app.post(
    "/api/v1/documents/{document_id}/embedding",
    response_model=Embedding,
    tags=["Embeddings"]
)
async def create_document_embedding(
    document_id: str,
    background_tasks: BackgroundTasks
) -> Embedding:
    """Cria embedding para um documento específico.

    Parameters
    ----------
    document_id : str
        ID do documento.
    background_tasks : BackgroundTasks
        Tarefas em background.

    Returns
    -------
    Embedding
        Embedding criado.

    Raises
    ------
    HTTPException
        Se o documento não for encontrado ou houver erro na criação.
    """
    try:
        # Buscar documento
        doc_result = await supabase.table('rag.01_base_conhecimento_regras_geral').select('*').eq('id', document_id).execute()

        if not doc_result.data:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        doc = doc_result.data[0]

        # Preparar texto para embedding
        content = json.dumps(doc['conteudo'], sort_keys=True)

        # Gerar embedding via API CoFlow
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.coflow.com.br/api/v1/embeddings',
                json={'text': content}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Erro ao gerar embedding")

            embedding_vector = response.json()['embedding']

        # Salvar embedding
        embedding_data = {
            'document_id': document_id,
            'embedding': embedding_vector,
            'content_hash': doc['content_hash']
        }

        # Verificar se já existe
        existing = await supabase.table('rag.02_embeddings_regras_geral').select('*').eq('document_id', document_id).execute()

        if existing.data:
            # Atualizar
            result = await supabase.table('rag.02_embeddings_regras_geral').update(embedding_data).eq('document_id', document_id).execute()
        else:
            # Inserir novo
            result = await supabase.table('rag.02_embeddings_regras_geral').insert(embedding_data).execute()

        # Registrar no changelog
        await supabase.rpc(
            'log_change',
            {
                'operation': 'SYNC',
                'table_name': 'rag.02_embeddings_regras_geral',
                'record_id': document_id,
                'new_data': embedding_data
            }
        ).execute()

        return Embedding(**result.data[0])

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

@app.post("/api/v1/embeddings/sync", response_model=BatchOperation, tags=["Embeddings"])
async def sync_missing_embeddings(background_tasks: BackgroundTasks) -> BatchOperation:
    """Sincroniza embeddings faltantes.

    Parameters
    ----------
    background_tasks : BackgroundTasks
        Tarefas em background.

    Returns
    -------
    BatchOperation
        Operação em lote criada.

    Raises
    ------
    HTTPException
        Se houver erro ao iniciar a sincronização.
    """
    try:
        # Criar registro de operação em lote
        batch_data = {
            'status': 'processing',
            'operation_type': 'sync_embeddings',
            'total_items': 0,
            'processed_items': 0,
            'errors': []
        }

        batch_result = await supabase.table('rag.batch_operations').insert(batch_data).execute()
        batch_id = batch_result.data[0]['id']

        # Iniciar processamento assíncrono
        background_tasks.add_task(process_missing_embeddings, batch_id)

        return BatchOperation(**batch_result.data[0])

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

async def process_missing_embeddings(batch_id: str) -> None:
    """Processa embeddings faltantes em background.

    Parameters
    ----------
    batch_id : str
        ID da operação em lote.
    """
    try:
        # Buscar documentos sem embedding
        query = '''
        SELECT d.* FROM rag.01_base_conhecimento_regras_geral d
        LEFT JOIN rag.02_embeddings_regras_geral e ON d.id = e.document_id
        WHERE e.id IS NULL
        '''

        docs = await supabase.rpc('execute_sql', {'query': query}).execute()

        if not docs.data:
            # Finalizar se não há documentos para processar
            await supabase.table('rag.batch_operations').update({
                'status': 'completed',
                'total_items': 0,
                'processed_items': 0
            }).eq('id', batch_id).execute()
            return

        total = len(docs.data)
        processed = 0
        errors = []

        # Atualizar total de itens
        await supabase.table('rag.batch_operations').update({
            'total_items': total
        }).eq('id', batch_id).execute()

        # Processar cada documento
        for doc in docs.data:
            try:
                # Gerar embedding
                content = json.dumps(doc['conteudo'], sort_keys=True)

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        'https://api.coflow.com.br/api/v1/embeddings',
                        json={'text': content}
                    )

                    if response.status_code != 200:
                        raise Exception("Erro ao gerar embedding")

                    embedding_vector = response.json()['embedding']

                # Salvar embedding
                embedding_data = {
                    'document_id': doc['id'],
                    'embedding': embedding_vector,
                    'content_hash': doc['content_hash']
                }

                await supabase.table('rag.02_embeddings_regras_geral').insert(embedding_data).execute()
                processed += 1

            except Exception as e:
                errors.append(f"Erro ao processar documento {doc['id']}: {e!s}")

            # Atualizar progresso
            await supabase.table('rag.batch_operations').update({
                'processed_items': processed,
                'errors': errors
            }).eq('id', batch_id).execute()

        # Finalizar processamento
        status = 'completed' if not errors else 'completed_with_errors'
        await supabase.table('rag.batch_operations').update({
            'status': status,
            'processed_items': processed,
            'errors': errors
        }).eq('id', batch_id).execute()

        # Atualizar estatísticas
        await supabase.rpc('update_statistics').execute()

    except Exception as err:
        # Registrar erro geral
        await supabase.table('rag.batch_operations').update({
            'status': 'failed',
            'errors': [str(err)]
        }).eq('id', batch_id).execute()

@app.get("/api/v1/documents/{document_id}/embedding/status", tags=["Embeddings"])
async def check_embedding_status(document_id: str = Path(...)) -> dict:
    """Verifica status do embedding de um documento.

    Parameters
    ----------
    document_id : str
        ID do documento.

    Returns
    -------
    dict
        Status do embedding.

    Raises
    ------
    HTTPException
        Se o documento não for encontrado.
    """
    try:
        # Buscar documento
        doc_result = await supabase.table('rag.01_base_conhecimento_regras_geral').select('*').eq('id', document_id).execute()

        if not doc_result.data:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Buscar embedding
        emb_result = await supabase.table('rag.02_embeddings_regras_geral').select('*').eq('document_id', document_id).execute()

        return {
            "document_id": document_id,
            "has_embedding": bool(emb_result.data),
            "content_hash": doc_result.data[0]['content_hash'],
            "embedding_hash": emb_result.data[0]['content_hash'] if emb_result.data else None,
            "needs_update": bool(emb_result.data) and doc_result.data[0]['content_hash'] != emb_result.data[0]['content_hash']
        }

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

@app.get("/api/v1/statistics", response_model=Statistics, tags=["Monitoramento"])
async def get_statistics() -> Statistics:
    """Retorna estatísticas atuais do sistema.

    Returns
    -------
    Statistics
        Estatísticas do sistema.

    Raises
    ------
    HTTPException
        Se houver erro ao buscar estatísticas.
    """
    try:
        # Buscar estatísticas atuais
        result = await supabase.table('rag.statistics').select('*').order('created_at', desc=True).limit(1).execute()

        if not result.data:
            # Se não houver estatísticas, gerar novas
            await supabase.rpc('update_statistics').execute()
            result = await supabase.table('rag.statistics').select('*').order('created_at', desc=True).limit(1).execute()

        return Statistics(**result.data[0])

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

@app.get("/api/v1/statistics/history", response_model=list[Statistics], tags=["Monitoramento"])
async def get_statistics_history(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
) -> list[Statistics]:
    """Retorna histórico de estatísticas.

    Parameters
    ----------
    start_date : Optional[datetime]
        Data inicial do período.
    end_date : Optional[datetime]
        Data final do período.

    Returns
    -------
    list[Statistics]
        Lista de estatísticas.

    Raises
    ------
    HTTPException
        Se houver erro ao buscar estatísticas.
    """
    try:
        query = supabase.table('rag.statistics').select('*')

        if start_date:
            query = query.gte('created_at', start_date.isoformat())
        if end_date:
            query = query.lte('created_at', end_date.isoformat())

        result = await query.order('created_at', desc=True).execute()

        return [Statistics(**item) for item in result.data]

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

@app.get("/api/v1/health", response_model=HealthCheck, tags=["Monitoramento"])
async def health_check() -> HealthCheck:
    """Verifica saúde do sistema.

    Returns
    -------
    HealthCheck
        Status de saúde do sistema.

    Raises
    ------
    HTTPException
        Se houver erro ao verificar saúde.
    """
    try:
        start_time = app.state.start_time

        # Verificar conexão com banco
        db_ok = False
        try:
            await supabase.table('rag.statistics').select('count', head=True).execute()
            db_ok = True
        except:
            pass

        return HealthCheck(
            status="healthy" if db_ok else "degraded",
            version="1.0.0",
            database_connection=db_ok,
            last_check=datetime.utcnow(),
            uptime=(datetime.utcnow() - start_time).total_seconds()
        )

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

@app.get("/api/v1/logs", response_model=list[LogEntry], tags=["Monitoramento"])
async def get_logs(
    operation_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100)
) -> list[LogEntry]:
    """Retorna logs do sistema.

    Parameters
    ----------
    operation_type : Optional[str]
        Tipo de operação para filtrar.
    start_date : Optional[datetime]
        Data inicial do período.
    end_date : Optional[datetime]
        Data final do período.
    limit : int
        Limite de registros.

    Returns
    -------
    list[LogEntry]
        Lista de logs.

    Raises
    ------
    HTTPException
        Se houver erro ao buscar logs.
    """
    try:
        query = supabase.table('rag.changelog').select('*')

        if operation_type:
            query = query.eq('operation_type', operation_type)
        if start_date:
            query = query.gte('created_at', start_date.isoformat())
        if end_date:
            query = query.lte('created_at', end_date.isoformat())

        result = await query.order('created_at', desc=True).limit(limit).execute()

        return [LogEntry(**item) for item in result.data]

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

@app.post("/api/v1/documents/batch", response_model=BatchOperation, tags=["Batch"])
async def batch_upload(
    documents: list[DocumentCreate],
    background_tasks: BackgroundTasks
) -> BatchOperation:
    """Upload em lote de documentos.

    Parameters
    ----------
    documents : list[DocumentCreate]
        Lista de documentos para upload.
    background_tasks : BackgroundTasks
        Tarefas em background.

    Returns
    -------
    BatchOperation
        Operação em lote criada.

    Raises
    ------
    HTTPException
        Se houver erro ao iniciar o upload.
    """
    try:
        # Criar registro da operação em lote
        batch_data = {
            'status': 'processing',
            'operation_type': 'batch_upload',
            'total_items': len(documents),
            'processed_items': 0,
            'errors': []
        }

        batch_result = await supabase.table('rag.batch_operations').insert(batch_data).execute()
        batch_id = batch_result.data[0]['id']

        # Iniciar processamento assíncrono
        background_tasks.add_task(process_batch_upload, batch_id, documents)

        return BatchOperation(**batch_result.data[0])

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

async def process_batch_upload(batch_id: str, documents: list[DocumentCreate]) -> None:
    """Processa upload em lote em background.

    Parameters
    ----------
    batch_id : str
        ID da operação em lote.
    documents : list[DocumentCreate]
        Lista de documentos para upload.
    """
    try:
        errors = []
        processed = 0

        for doc in documents:
            try:
                # Processar cada documento
                content = json.dumps(doc.conteudo, sort_keys=True)
                content_hash = hashlib.sha256(content.encode()).hexdigest()

                # Verificar duplicidade
                result = await supabase.rpc('check_duplicate_content', {'content_hash': content_hash}).execute()
                if result.data:
                    errors.append(f"Documento duplicado: {doc.titulo}")
                    continue

                # Inserir documento
                doc_data = {
                    'titulo': doc.titulo,
                    'conteudo': doc.conteudo,
                    'content_hash': content_hash,
                    'metadata': doc.metadata or {}
                }

                result = await supabase.table('rag.01_base_conhecimento_regras_geral').insert(doc_data).execute()

                if result.data:
                    # Registrar no changelog
                    await supabase.rpc(
                        'log_change',
                        {
                            'operation': 'BATCH_CREATE',
                            'table_name': 'rag.01_base_conhecimento_regras_geral',
                            'record_id': str(result.data[0]['id']),
                            'new_data': doc_data
                        }
                    ).execute()

                    processed += 1
                else:
                    errors.append(f"Erro ao inserir documento: {doc.titulo}")

            except Exception as e:
                errors.append(f"Erro ao processar {doc.titulo}: {e!s}")

            # Atualizar progresso
            await supabase.table('rag.batch_operations').update({
                'processed_items': processed,
                'errors': errors
            }).eq('id', batch_id).execute()

        # Finalizar processamento
        status = 'completed' if not errors else 'completed_with_errors'
        await supabase.table('rag.batch_operations').update({
            'status': status,
            'processed_items': processed,
            'errors': errors
        }).eq('id', batch_id).execute()

        # Atualizar estatísticas
        await supabase.rpc('update_statistics').execute()

    except Exception as err:
        # Registrar erro geral
        await supabase.table('rag.batch_operations').update({
            'status': 'failed',
            'errors': [str(err)]
        }).eq('id', batch_id).execute()

@app.get("/api/v1/documents/batch/{batch_id}", response_model=BatchOperation, tags=["Batch"])
async def get_batch_status(batch_id: str = Path(...)) -> BatchOperation:
    """Retorna status de uma operação em lote.

    Parameters
    ----------
    batch_id : str
        ID da operação em lote.

    Returns
    -------
    BatchOperation
        Status da operação.

    Raises
    ------
    HTTPException
        Se a operação não for encontrada.
    """
    try:
        result = await supabase.table('rag.batch_operations').select('*').eq('id', batch_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Operação em lote não encontrada")

        return BatchOperation(**result.data[0])

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a requisição"
        ) from err

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
>>>>>>> Stashed changes
