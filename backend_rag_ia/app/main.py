"""Módulo principal da aplicação.

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

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/documents/", response_model=DocumentResponse)
async def create_document(document: DocumentCreate):
    """Cria um novo documento na base de conhecimento.

    Parameters
    ----------
    document : DocumentCreate
        Dados do documento a ser criado.

    Returns
    -------
    DocumentResponse
        Documento criado.

    Raises
    ------
    HTTPException
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
    """Busca um documento por ID.

    Parameters
    ----------
    document_id : str
        ID do documento a ser buscado.

    Returns
    -------
    DocumentResponse
        Documento encontrado.

    Raises
    ------
    HTTPException
        Se o documento não for encontrado.

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

        if not result.data:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Buscar embedding associado
        embedding = await (
            supabase.table(TABELA_EMBEDDINGS)
            .select('*')
            .eq('document_id', document_id)
            .execute()
        )

        # Adicionar status do embedding aos metadados
        doc = result.data[0]
        doc['metadata'] = doc.get('metadata', {})
        doc['metadata']['has_embedding'] = bool(embedding.data)

        return DocumentResponse(**doc)

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err

@app.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(document_id: str, document: DocumentUpdate):
    """Atualiza um documento existente.

    Parameters
    ----------
    document_id : str
        ID do documento a ser atualizado.
    document : DocumentUpdate
        Dados para atualização do documento.

    Returns
    -------
    DocumentResponse
        Documento atualizado.

    Raises
    ------
    HTTPException
        Se o documento não for encontrado ou houver erro na atualização.

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

        if not existing.data:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Preparar dados para atualização
        update_data = document.dict(exclude_unset=True)

        if 'conteudo' in update_data:
            # Gerar novo hash se conteúdo foi atualizado
            content_hash = document.generate_hash()
            update_data['content_hash'] = content_hash

        # Atualizar documento
        result = await (
            supabase.table(TABELA_BASE_CONHECIMENTO)
            .update(update_data)
            .eq('id', document_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=500, detail="Erro ao atualizar documento")

        return DocumentResponse(**result.data[0])

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Remove um documento existente.

    Parameters
    ----------
    document_id : str
        ID do documento a ser removido.

    Returns
    -------
    dict
        Mensagem de confirmação.

    Raises
    ------
    HTTPException
        Se o documento não for encontrado ou houver erro na remoção.

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

        if not existing.data:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        # Remover embedding primeiro (se existir)
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

        if not result.data:
            raise HTTPException(status_code=500, detail="Erro ao remover documento")

        return {"message": "Documento removido com sucesso"}

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err
