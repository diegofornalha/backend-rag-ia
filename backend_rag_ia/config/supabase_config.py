from typing import List, Dict, Any
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseConfig:
    def __init__(self):
        self.url: str = os.getenv("SUPABASE_URL", "")
        self.key: str = os.getenv("SUPABASE_KEY", "")
        self.client: Client = create_client(self.url, self.key)

    def generate_embedding(self, text: str) -> List[float]:
        """Gera embedding para o texto usando função RPC do Supabase."""
        try:
            response = self.client.rpc(
                "generate_embedding",
                {"input_text": text}
            ).execute()
            return response.data
        except Exception as e:
            print(f"Erro ao gerar embedding: {e}")
            return []

    def match_documents(self, query_embedding: List[float], match_threshold: float = 0.7) -> List[Dict[Any, Any]]:
        """Busca documentos similares usando função RPC do Supabase."""
        try:
            response = self.client.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": match_threshold,
                    "match_count": 10
                }
            ).execute()
            return response.data
        except Exception as e:
            print(f"Erro na busca de documentos: {e}")
            return []

    def search_documents(self, query: str) -> List[Dict[Any, Any]]:
        """Realiza busca semântica completa."""
        try:
            embedding = self.generate_embedding(query)
            if not embedding:
                return []
            
            return self.match_documents(embedding)
        except Exception as e:
            print(f"Erro na busca semântica: {e}")
            return [] 