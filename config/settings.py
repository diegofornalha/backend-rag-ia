from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações do Modelo
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Configurações do Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_PROJECT_ID: Optional[str] = None
    
    # Configurações de Ambiente
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Configurações de Cache
    CACHE_TTL: int = 3600  # 1 hora
    MAX_CACHE_SIZE: int = 1000
    
    # Configurações de Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # 1 minuto
    
    # Configurações de Similaridade
    SIMILARITY_THRESHOLD: float = 0.5
    MAX_RESULTS: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True 