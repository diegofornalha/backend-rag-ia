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

class LocalConfig(BaseSettings):
    """Configurações para ambiente local"""
    ENVIRONMENT: str = "local"
    DOCUMENTS_COUNT: int = 3
    EMBEDDINGS_COUNT: int = 3
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

class ProductionConfig(BaseSettings):
    """Configurações para ambiente de produção"""
    ENVIRONMENT: str = "production"
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
    DEBUG: bool = False

class TestConfig(BaseSettings):
    """Configurações para ambiente de teste"""
    ENVIRONMENT: str = "test"
    DOCUMENTS_COUNT: int = 0
    EMBEDDINGS_COUNT: int = 0
    SUPABASE_URL: str = "test_url"
    SUPABASE_KEY: str = "test_key"
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    DEBUG: bool = True

@lru_cache()
def get_settings() -> BaseSettings:
    """Retorna as configurações do ambiente atual"""
    env = os.getenv("ENVIRONMENT", "local").lower()
    configs = {
        "local": LocalConfig,
        "production": ProductionConfig,
        "test": TestConfig
    }
    config_class = configs.get(env, LocalConfig)
    return config_class() 