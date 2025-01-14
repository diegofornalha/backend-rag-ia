"""
Rotas de chat do sistema.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...services.chat_system import ChatSystem


class ChatMessage(BaseModel):
    """Modelo de mensagem do chat."""
    message: str
    history: List[dict] = []
    documentIds: List[str] = []


class DocumentValidation(BaseModel):
    """Modelo para validação de documento."""
    content: str
    cliente: str


chat_router = APIRouter(prefix="/api/chat", tags=["chat"])
chat_system = ChatSystem()


@chat_router.post("/clientes")
async def chat_with_documents(message: ChatMessage):
    """
    Processa uma mensagem do chat com documentos.
    """
    try:
        response = await chat_system.process_message(
            message=message.message,
            context={
                "history": message.history,
                "documents": message.documentIds,
                "is_upload": False
            }
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/documents/validate")
async def validate_document(data: DocumentValidation):
    """
    Valida um documento antes do upload.
    """
    try:
        response = await chat_system.validate_document(
            content=data.content,
            cliente=data.cliente
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/status")
def get_chat_status():
    """
    Retorna o status atual do sistema de chat.
    """
    try:
        return chat_system.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 