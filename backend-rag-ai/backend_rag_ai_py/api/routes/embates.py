from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ...embates.models.embate_models import DefaultEmbateContext, DefaultEmbateResult
from ...embates.processor.content_processor import process_content

router = APIRouter(prefix="/api/embates")

class ProcessContentRequest(BaseModel):
    content: str
    metadata: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None

@router.post("/process")
async def process_content_endpoint(request: ProcessContentRequest):
    try:
        # Criar contexto do embate
        context = DefaultEmbateContext.create(
            embate_id=f"content-{hash(request.content)}",
            parameters=request.parameters or {},
            metadata=request.metadata
        )
        
        # Processar conteúdo
        result = await process_content(context, request.content)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail={"errors": result.errors}
            )
            
        return result.data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 