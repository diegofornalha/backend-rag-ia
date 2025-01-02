import logging
import os

from dotenv import load_dotenv
from supabase import create_client

# Configurando logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregando variáveis de ambiente
load_dotenv()

def test_supabase_connection():
    """Testa a conexão básica com o Supabase."""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        client = create_client(url, key)
        
        # Tenta uma operação simples
        response = client.table("documentos").select("id").limit(1).execute()
        logger.info("✅ Conexão com Supabase estabelecida com sucesso - %d registros encontrados", len(response.data))
        return True
    except Exception as e:
        logger.error("❌ Erro na conexão com Supabase: %s", str(e))
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