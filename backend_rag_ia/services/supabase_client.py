"""
Módulo para gerenciar a conexão com o Supabase.
"""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseManager:
    """Gerencia a conexão com o Supabase."""

    _instance: Optional["SupabaseManager"] = None
    _client: Optional[Client] = None

    def __new__(cls) -> "SupabaseManager":
        """Implementa o padrão Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Inicializa o cliente Supabase."""
        if self._client is None:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

            if not supabase_url or not supabase_key:
                raise ValueError(
                    "SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env"
                )

            self._client = create_client(supabase_url, supabase_key)

    @property
    def client(self) -> Client:
        """Retorna o cliente Supabase."""
        if self._client is None:
            raise RuntimeError("Cliente Supabase não foi inicializado")
        return self._client


# Instância global do cliente Supabase
supabase = SupabaseManager().client
