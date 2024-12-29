from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

class Settings:
    """Configurações da API Gemini."""
    
    # Configurações do Flask
    DEBUG: bool = os.getenv("FLASK_DEBUG", "1") == "1"
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Configurações da API
    APP_NAME: str = os.getenv("APP_NAME", "Gemini API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Configuração do Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    
    # Configuração do Swagger
    SWAGGER_URL: str = os.getenv("SWAGGER_URL", "/docs")
    API_URL: str = os.getenv("API_URL", "/swagger")

# Instância global das configurações
settings = Settings() 