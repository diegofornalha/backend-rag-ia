from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Verifica a saúde da API do Evolution."""
    return {
        "status": "healthy",
        "service": "evolution"
    } 