import logging
import os

import requests
from dotenv import load_dotenv

# Configurando logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregando variáveis de ambiente
load_dotenv()

def test_supabase_connection():
    """Testa a conexão básica com o Supabase usando requisições HTTP."""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            logger.error("❌ Variáveis de ambiente SUPABASE_URL ou SUPABASE_KEY não configuradas")
            return False
        
        # Monta a URL para a tabela documentos
        api_url = f"{url}/rest/v1/documentos?select=id&limit=1"
        
        # Configura os headers necessários
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }
        
        # Faz a requisição
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            logger.info("✅ Conexão com Supabase estabelecida com sucesso")
            return True
        else:
            logger.error(f"❌ Erro na conexão com Supabase. Status code: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro na conexão com Supabase: {e}")
        return False

def main():
    """Executa teste de conexão com Supabase."""
    logger.info("🔍 Iniciando teste de conexão com Supabase...")
    
    if test_supabase_connection():
        logger.info("✨ Teste de conexão completado com sucesso")
    else:
        logger.error("⚠️ Falha no teste de conexão")

if __name__ == "__main__":
    main() 