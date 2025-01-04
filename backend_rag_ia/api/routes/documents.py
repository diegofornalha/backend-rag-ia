"""Módulo para rotas de documentos da API.

Este módulo fornece endpoints para gerenciamento de documentos,
incluindo upload, listagem, busca e remoção.
"""

from typing import Optional

from fastapi import APIRouter, File, Query, UploadFile
from pydantic import BaseModel

from ...services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentResponse(BaseModel):
    """Modelo de resposta para documentos.

    Attributes
    ----------
    id : str
        Identificador único do documento.
    title : str
        Título do documento.
    content : str
        Conteúdo do documento.
    metadata : dict
        Metadados do documento.

    """

    id: str
    title: str
    content: str
    metadata: dict


@router.post("/", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    metadata: Optional[dict] = None
) -> DocumentResponse:
    """Faz upload de um novo documento.

    Parameters
    ----------
    file : UploadFile
        Arquivo a ser enviado.
    title : Optional[str]
        Título do documento.
    metadata : Optional[dict]
        Metadados do documento.

    Returns
    -------
    DocumentResponse
        Documento criado.

    """
    service = DocumentService()
    document = await service.upload_document(file, title, metadata)
    return document


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
) -> list[DocumentResponse]:
    """Lista documentos com paginação.

    Parameters
    ----------
    skip : int
        Número de documentos para pular.
    limit : int
        Número máximo de documentos a retornar.

    Returns
    -------
    list[DocumentResponse]
        Lista de documentos.

    """
    service = DocumentService()
    documents = await service.list_documents(skip, limit)
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str) -> DocumentResponse:
    """Busca um documento pelo ID.

    Parameters
    ----------
    document_id : str
        ID do documento.

    Returns
    -------
    DocumentResponse
        Documento encontrado.

    """
    service = DocumentService()
    document = await service.get_document(document_id)
    return document


@router.delete("/{document_id}")
async def delete_document(document_id: str) -> dict:
    """Remove um documento.

    Parameters
    ----------
    document_id : str
        ID do documento.

    Returns
    -------
    dict
        Mensagem de confirmação.

    """
    service = DocumentService()
    await service.delete_document(document_id)
    return {"message": "Documento removido com sucesso"}
