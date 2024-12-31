import sys
from pathlib import Path
import logging
import os
from dotenv import load_dotenv

# Configurando logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregando variáveis de ambiente
load_dotenv()

def test_env_vars():
    """Testa se as variáveis de ambiente estão configuradas."""
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Variáveis de ambiente faltando: {missing_vars}")
        return False
    
    logger.info("✅ Variáveis de ambiente configuradas corretamente")
    return True

def main():
    """Executa testes básicos de configuração."""
    logger.info("🔍 Iniciando testes de configuração básica...")
    
    if not test_env_vars():
        logger.error("⚠️ Falha na verificação das variáveis de ambiente")
        return
    
    logger.info("✨ Testes básicos completados")

if __name__ == "__main__":
    main() 