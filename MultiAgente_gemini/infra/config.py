"""
Configurações do sistema Gemini.
"""

import os
from dotenv import load_dotenv

class Config:
    """Gerencia configurações do sistema."""
    
    def __init__(self):
        """Inicializa carregando variáveis de ambiente."""
        load_dotenv()
    
    def get_api_key(self) -> str:
        """Obtém a chave da API do Gemini."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no ambiente")
        return api_key 