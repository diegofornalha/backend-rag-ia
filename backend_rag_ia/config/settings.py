from functools import lru_cache
from typing import Literal
import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configurações da aplicação usando variáveis de ambiente.
    """
    # API
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "RAG API"
    API_DESCRIPTION: str = "API para busca semântica de documentos"
    
    # CORS - Lista branca de origens por ambiente
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"  # Default para desenvolvimento
    
    # Supabase - Sem valores padrão para produção
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Ambiente
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # Modo de Operação
    OPERATION_MODE: Literal["local", "render", "auto"] = "auto"
    RENDER_URL: str = "https://rag-api.onrender.com"
    LOCAL_URL: str = "http://localhost:10000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Permite variáveis extras

    @property
    def is_render_environment(self) -> bool:
        """Verifica se está rodando no ambiente Render."""
        return self.OPERATION_MODE == "render" or self.ENVIRONMENT == "render"
    
    @property
    def active_url(self) -> str:
        """Retorna a URL ativa baseada no modo de operação."""
        if self.is_render_environment:
            return self.RENDER_URL
        return self.LOCAL_URL
        
    @property
    def cors_origins_list(self) -> list[str]:
        """
        Retorna a lista de origens permitidas baseada no ambiente.
        Em produção, usa apenas as origens explicitamente configuradas.
        Em desenvolvimento, inclui origens locais adicionais.
        """
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        
        # Em modo debug, adiciona origens locais comuns
        if self.DEBUG:
            origins.extend([
                "http://localhost:3000",  # React
                "http://localhost:8000",  # Django
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000"
            ])
            
        return list(set(origins))  # Remove duplicatas

@lru_cache
def get_settings() -> Settings:
    """
    Retorna as configurações da aplicação.
    Usa cache para evitar múltiplas leituras do arquivo .env
    """
    try:
        return Settings()
    except Exception as e:
        if "render" in str(os.getenv("OPERATION_MODE", "")).lower():
            # Em ambiente Render, deixa a validação para runtime
            return Settings.construct()
        raise e 