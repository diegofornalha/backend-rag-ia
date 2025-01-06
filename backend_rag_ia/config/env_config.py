"""
Configuração centralizada para gerenciamento de variáveis de ambiente e configurações do sistema.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


@dataclass
class SupabaseCredentials:
    """Credenciais do Supabase."""

    url: str
    anon_key: str
    service_key: str
    db_url: str
    jwt_secret: str


@dataclass
class APIConfig:
    """Configurações da API."""

    host: str = "0.0.0.0"
    port: int = 10000
    base_url: str = "http://localhost:10000"
    api_version: str = "v1"
    operation_mode: str = "local"


@dataclass
class AIConfig:
    """Configurações de serviços de IA."""

    gemini_key: str
    langchain_key: str
    langchain_endpoint: str
    langchain_project: str


class EnvConfig:
    """Gerenciador centralizado de configurações."""

    def __init__(self) -> None:
        """Inicializa as configurações."""
        self.supabase = self._load_supabase_config()
        self.api = self._load_api_config()
        self.ai = self._load_ai_config()
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "true").lower() == "true"

    def _load_supabase_config(self) -> SupabaseCredentials:
        """Carrega configurações do Supabase."""
        return SupabaseCredentials(
            url=os.getenv("SUPABASE_URL", ""),
            anon_key=os.getenv("SUPABASE_KEY", ""),
            service_key=os.getenv("SUPABASE_SERVICE_KEY", ""),
            db_url=os.getenv("SUPABASE_DB_URL", ""),
            jwt_secret=os.getenv("SUPABASE_JWT_SECRET", ""),
        )

    def _load_api_config(self) -> APIConfig:
        """Carrega configurações da API."""
        operation_mode = os.getenv("OPERATION_MODE", "local")
        active_url = os.getenv("ACTIVE_URL", "")
        local_url = os.getenv("LOCAL_URL", "http://localhost:10000")

        # Se estiver em modo local ou não tiver ACTIVE_URL, usa LOCAL_URL
        base_url = active_url if (operation_mode != "local" and active_url) else local_url

        return APIConfig(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "10000")),
            base_url=base_url,
            api_version=os.getenv("API_VERSION", "v1"),
            operation_mode=operation_mode,
        )

    def _load_ai_config(self) -> AIConfig:
        """Carrega configurações dos serviços de IA."""
        return AIConfig(
            gemini_key=os.getenv("GEMINI_API_KEY", ""),
            langchain_key=os.getenv("LANGCHAIN_API_KEY", ""),
            langchain_endpoint=os.getenv("LANGCHAIN_ENDPOINT", ""),
            langchain_project=os.getenv("LANGCHAIN_PROJECT", ""),
        )

    def get_supabase_key(self, require_service_key: bool = False) -> str | None:
        """
        Retorna a chave apropriada do Supabase baseado no contexto.

        Args:
            require_service_key: Se True, retorna apenas a service_key

        Returns:
            str: Chave do Supabase ou None se não encontrada
        """
        if require_service_key:
            return self.supabase.service_key
        return self.supabase.service_key or self.supabase.anon_key

    def get_gemini_key(self) -> str:
        """
        Retorna a chave da API do Gemini.

        Returns:
            str: Chave da API do Gemini

        Raises:
            ValueError: Se a chave não estiver configurada
        """
        if not self.ai.gemini_key:
            raise ValueError("Chave da API do Gemini não configurada")
        return self.ai.gemini_key

    def get_api_url(self, endpoint: str = "") -> str:
        """
        Constrói a URL da API com o endpoint especificado.

        Args:
            endpoint: Endpoint da API (opcional)

        Returns:
            str: URL completa da API
        """
        base = f"{self.api.base_url}/api/{self.api.api_version}"
        return f"{base}/{endpoint.lstrip('/')}" if endpoint else base

    def validate(self) -> bool:
        """
        Valida se todas as configurações necessárias estão presentes.

        Returns:
            bool: True se todas as configurações estão válidas
        """
        required_configs = [
            (self.supabase.url, "SUPABASE_URL"),
            (
                self.supabase.service_key or self.supabase.anon_key,
                "SUPABASE_KEY ou SUPABASE_SERVICE_KEY",
            ),
            (self.api.base_url, "ACTIVE_URL ou LOCAL_URL"),
            (self.ai.gemini_key, "GEMINI_API_KEY"),
        ]

        for value, name in required_configs:
            if not value:
                print(f"❌ Configuração ausente: {name}")
                return False
        return True


# Instância global de configuração
config = EnvConfig()
