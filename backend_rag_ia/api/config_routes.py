from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from ..services.llm_services.providers.gemini import GeminiProvider
from ..services.agent_services.coordinator import AgentCoordinator
from ..services.suggestion_services.interfaces import SuggestionInterface
from ..services.embedding_services.vector_store import VectorStore

router = APIRouter()

def get_vector_store():
    return VectorStore()

def get_llm_provider():
    return GeminiProvider()

def get_agent_coordinator(
    llm_provider: GeminiProvider = Depends(get_llm_provider),
    vector_store: VectorStore = Depends(get_vector_store)
):
    return AgentCoordinator(llm_provider=llm_provider, vector_store=vector_store)

@router.post("/analyze")
async def analyze_content(
    content: Dict[str, Any],
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    try:
        # Primeiro, armazena o conteúdo no vector store
        vector_store = get_vector_store()
        embeddings = await vector_store.store_content(content["text"])
        
        # Usa o multi-agente para análise
        result = await coordinator.process_task({
            "type": "analysis",
            "content": content["text"],
            "embeddings": embeddings
        })
        
        return {
            "status": "success",
            "result": result,
            "embeddings_stored": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions/{query}")
async def get_suggestions(
    query: str,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    try:
        # Busca conteúdo similar usando embeddings
        vector_store = get_vector_store()
        similar_content = await vector_store.search_similar(query)
        
        # Usa o multi-agente para gerar sugestões
        result = await coordinator.process_task({
            "type": "suggestion",
            "query": query,
            "similar_content": similar_content
        })
        
        return {
            "status": "success",
            "suggestions": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def configure_routes(app):
    app.include_router(router, prefix="/api/v1", tags=["content"])
