"""
Módulo para gerenciar a conexão com o Supabase.
"""
import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv
from config.config import get_settings

load_dotenv()

class SupabaseManager:
    """Gerencia a conexão com o Supabase."""
    
    _instance: Optional['SupabaseManager'] = None
    _client: Optional[Client] = None
    
    def __new__(cls) -> 'SupabaseManager':
        """Implementa o padrão Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Inicializa o cliente Supabase."""
        if self._client is None:
            settings = get_settings()
            supabase_url = settings.SUPABASE_URL
            supabase_key = settings.SUPABASE_KEY
            
            if not supabase_url or not supabase_key:
                raise ValueError(
                    "SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env"
                )
            
            try:
                self._client = create_client(supabase_url, supabase_key)
            except Exception as e:
                raise RuntimeError(f"Erro ao criar cliente Supabase: {str(e)}")
    
    @property
    def client(self) -> Client:
        """Retorna o cliente Supabase."""
        if self._client is None:
            raise RuntimeError("Cliente Supabase não foi inicializado")
        return self._client

def create_supabase_client() -> Client:
    """Cria e retorna um cliente Supabase."""
    try:
        return SupabaseManager().client
    except Exception as e:
        raise RuntimeError(f"Erro ao obter cliente Supabase: {str(e)}")

# Instância global do cliente Supabase
try:
    supabase = create_supabase_client()
except Exception as e:
    print(f"⚠️ Aviso: Não foi possível inicializar o cliente Supabase: {str(e)}")
    supabase = None 