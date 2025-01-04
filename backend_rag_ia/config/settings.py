<<<<<<< Updated upstream
"""Implementa configuração da aplicação.
=======
"""Módulo de configuração da aplicação.
>>>>>>> Stashed changes

Este módulo fornece as configurações da aplicação através de variáveis de ambiente.
"""

import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
<<<<<<< Updated upstream
    """Define configurações da aplicação usando variáveis de ambiente.
=======
    """Configurações da aplicação usando variáveis de ambiente.
>>>>>>> Stashed changes

    Esta classe gerencia todas as configurações da aplicação, incluindo
    configurações da API, CORS, Supabase e ambiente de execução.

    Attributes
    ----------
    API_VERSION : str
        Versão da API.
    API_TITLE : str
        Título da API.
    API_DESCRIPTION : str
        Descrição da API.
    CORS_ORIGINS : str
        Lista de origens permitidas para CORS, separadas por vírgula.
    SUPABASE_URL : str
        URL do Supabase.
    SUPABASE_KEY : str
        Chave de acesso do Supabase.
    ENVIRONMENT : str
        Ambiente de execução ('production', 'development' ou 'preview').
    DEBUG : bool
        Modo de debug.
    OPERATION_MODE : str
        Modo de operação ('local', 'render' ou 'auto').
    RENDER_URL : str
        URL do ambiente Render.
    LOCAL_URL : str
        URL do ambiente local.

    """

    # API
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "RAG API"
    API_DESCRIPTION: str = "API para busca semântica de documentos"

    # CORS - Lista branca de origens por ambiente
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"  # Default para desenvolvimento

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Ambiente
    ENVIRONMENT: Literal["production", "development", "preview"] = "production"
    DEBUG: bool = False

    # Modo de Operação
    OPERATION_MODE: Literal["local", "render", "auto"] = "auto"
    RENDER_URL: str = "https://rag-api.onrender.com"
    LOCAL_URL: str = "http://localhost:10000"

    class Config:
<<<<<<< Updated upstream
        """Define configurações do Pydantic.
=======
        """Configurações do Pydantic.
>>>>>>> Stashed changes

        Attributes
        ----------
        env_file : str
            Arquivo de variáveis de ambiente.
        case_sensitive : bool
            Se as variáveis são case sensitive.
        extra : str
            Permite variáveis extras.

        """
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Permite variáveis extras

    @property
    def is_render_environment(self) -> bool:
        """Verifica se está rodando no ambiente Render.

        Returns
        -------
        bool
            True se estiver rodando no ambiente Render, False caso contrário.

        """
        return self.OPERATION_MODE == "render" or self.ENVIRONMENT in ["render", "preview"]

    @property
    def is_preview_environment(self) -> bool:
        """Verifica se está rodando em um ambiente de preview.

        Returns
        -------
        bool
            True se estiver rodando em ambiente de preview, False caso contrário.

        """
        return self.ENVIRONMENT == "preview"

    @property
    def active_url(self) -> str:
        """Retorna a URL ativa baseada no modo de operação.

        Returns
        -------
        str
            URL ativa para o ambiente atual.

        """
        if self.is_render_environment:
            # Se for preview, usa a URL do preview
            if self.is_preview_environment:
                preview_url = os.getenv("RENDER_PREVIEW_URL")
                if preview_url:
                    return preview_url
            return self.RENDER_URL
        return self.LOCAL_URL

    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna a lista de origens permitidas baseada no ambiente.

        Em produção, usa apenas as origens explicitamente configuradas.
        Em desenvolvimento ou preview, inclui origens locais adicionais.

        Returns
        -------
        list[str]
            Lista de origens permitidas para CORS.

        """
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

        # Em modo debug ou preview, adiciona origens locais comuns
        if self.DEBUG or self.is_preview_environment:
            origins.extend([
                "http://localhost:3000",  # React
                "http://localhost:8000",  # Django
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000"
            ])

        return list(set(origins))  # Remove duplicatas


@lru_cache
def get_settings() -> Settings:
    """Retorna as configurações da aplicação.

    Usa cache para evitar múltiplas leituras do arquivo .env.

    Returns
    -------
    Settings
        Instância das configurações da aplicação.

    Raises
    ------
    Exception
        Se houver erro ao carregar as configurações fora do ambiente Render/preview.

    """
    try:
        return Settings()
    except Exception as e:
        if "render" in str(os.getenv("OPERATION_MODE", "")).lower() or \
           os.getenv("ENVIRONMENT") == "preview":
            # Em ambiente Render ou preview, deixa a validação para runtime
            return Settings.construct()
        raise e
