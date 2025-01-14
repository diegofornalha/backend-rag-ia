import uvicorn
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

from backend_rag_ai_py.main import app

if __name__ == "__main__":
    uvicorn.run(
        "backend_rag_ai_py.main:app",
        host="0.0.0.0",
        port=10000,
        reload=True  # Habilita hot-reload para desenvolvimento
    ) 