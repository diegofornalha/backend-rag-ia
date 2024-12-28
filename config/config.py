from typing import Dict, Any
from pydantic_settings import BaseSettings
import os
from functools import lru_cache
from dotenv import load_dotenv

def load_env():
    """Carrega as variáveis de ambiente apropriadas"""
    env = os.getenv("ENVIRONMENT", "local").lower()
    if env == "local" and os.path.exists(".env.local"):
        load_dotenv(".env.local")
    else:
        load_dotenv()

# Carrega as variáveis de ambiente
load_env()

class Settings(BaseSettings):
    """Configurações base compartilhadas"""
    ENVIRONMENT: str = "local"
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    DEBUG: bool = False
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_PROJECT_ID: str | None = None
    
    # Configurações do Modelo
    EMBEDDING_DIM: int = 384
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
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

class LocalConfig(Settings):
    """Configurações para ambiente local"""
    ENVIRONMENT: str = "local"
    DOCUMENTS_COUNT: int = 3
    EMBEDDINGS_COUNT: int = 3
    DEBUG: bool = True

class ProductionConfig(Settings):
    """Configurações para ambiente de produção"""
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

class TestConfig(Settings):
    """Configurações para ambiente de teste"""
    ENVIRONMENT: str = "test"
    DOCUMENTS_COUNT: int = 0
    EMBEDDINGS_COUNT: int = 0
    SUPABASE_URL: str = "test_url"
    SUPABASE_KEY: str = "test_key"
    DEBUG: bool = True

@lru_cache()
def get_settings() -> Settings:
    """Retorna as configurações do ambiente atual"""
    env = os.getenv("ENVIRONMENT", "local").lower()
    configs = {
        "local": LocalConfig,
        "production": ProductionConfig,
        "test": TestConfig
    }
    
    config_class = configs.get(env, LocalConfig)
    return config_class(
        SUPABASE_URL=os.getenv("SUPABASE_URL", ""),
        SUPABASE_KEY=os.getenv("SUPABASE_KEY", "")
    ) 