"""Rotas de conversão."""

from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/convert", tags=["convert"])

class MarkdownRequest(BaseModel):
    content: str

class MarkdownResponse(BaseModel):
    html: str
    metadata: dict[str, Any] = {}

@router.post("/markdown")
async def convert_markdown(request: MarkdownRequest) -> MarkdownResponse:
    """Converte markdown para HTML.

    Args:
        request: Conteúdo markdown para converter

    Returns:
        HTML convertido e metadados
    """
    try:
        # TODO: Implementar lógica de conversão
        return MarkdownResponse(
            html=f"<p>{request.content}</p>",
            metadata={"format": "html"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 