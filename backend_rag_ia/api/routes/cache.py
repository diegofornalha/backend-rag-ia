from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ...cache.distributed_cache import DistributedCache

router = APIRouter(prefix="/cache", tags=["Cache"])
cache = DistributedCache()

@router.get("/health")
async def check_cache_health() -> Dict[str, Any]:
    """
    Verifica saúde do cache distribuído
    
    Returns:
        Dicionário com status e estatísticas
    """
    try:
        # Testa operações básicas
        test_key = "health_check"
        test_value = {"status": "ok", "timestamp": "2024-01-20T12:00:00"}
        
        # Set
        set_ok = cache.set(test_key, test_value)
        if not set_ok:
            raise HTTPException(
                status_code=500,
                detail="Falha ao armazenar no cache"
            )
        
        # Get
        stored_value = cache.get(test_key)
        if not stored_value:
            raise HTTPException(
                status_code=500,
                detail="Falha ao recuperar do cache"
            )
        
        # Delete
        delete_ok = cache.delete(test_key)
        if not delete_ok:
            raise HTTPException(
                status_code=500,
                detail="Falha ao limpar cache"
            )
        
        # Obtém estatísticas
        stats = cache.get_stats()
        
        return {
            "status": "healthy",
            "operations": {
                "set": set_ok,
                "get": stored_value == test_value,
                "delete": delete_ok
            },
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar cache: {str(e)}"
        ) 