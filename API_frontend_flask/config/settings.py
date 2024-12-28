from typing import Dict, Any
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Settings:
    """Configurações do Flask Frontend."""
    
    # Configurações básicas
    TITLE: str = "Frontend Flask RAG"
    DESCRIPTION: str = "Interface web para o sistema RAG"
    VERSION: str = "1.0.0"
    
    # Configurações do Flask
    DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    PORT: int = int(os.getenv("FLASK_PORT", "5001"))
    HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "your-secret-key")
    
    # Configurações de template
    TEMPLATE_FOLDER: str = "templates"
    STATIC_FOLDER: str = "static"
    STATIC_URL_PATH: str = "/static"
    
    # Configurações de API
    RAG_API_URL: str = os.getenv("RAG_API_URL", "http://localhost:5000")
    
    def get_config(self) -> Dict[str, Any]:
        """Retorna as configurações como dicionário."""
        return {
            "TITLE": self.TITLE,
            "DESCRIPTION": self.DESCRIPTION,
            "VERSION": self.VERSION,
            "DEBUG": self.DEBUG,
            "SECRET_KEY": self.SECRET_KEY,
            "RAG_API_URL": self.RAG_API_URL
        }

# Instância global das configurações
settings = Settings() 