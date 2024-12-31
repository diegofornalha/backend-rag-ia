from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal, List

class Settings(BaseSettings):
    """
    Configurações da aplicação usando variáveis de ambiente.
    """
    # API
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "RAG API"
    API_DESCRIPTION: str = "API para busca semântica de documentos"
    
    # Supabase
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
        return self.ENVIRONMENT == "render"
    
    @property
    def active_url(self) -> str:
        """Retorna a URL ativa baseada no modo de operação."""
        if self.OPERATION_MODE == "render":
            return self.RENDER_URL
        elif self.OPERATION_MODE == "local":
            return self.LOCAL_URL
        # Modo auto - tenta local primeiro, depois Render
        return self.LOCAL_URL

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna as configurações da aplicação.
    Usa cache para evitar múltiplas leituras do arquivo .env
    """
    return Settings() 