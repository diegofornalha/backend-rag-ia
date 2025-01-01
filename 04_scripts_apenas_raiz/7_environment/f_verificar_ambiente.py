import sys
import pkg_resources
import platform
import logging

# Configurando logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_python_version():
    """Verifica a versão do Python."""
    version = sys.version_info
    logger.info(f"Python version: {version.major}.{version.minor}.{version.micro}")
    logger.info(f"Platform: {platform.platform()}")
    return version.major == 3 and version.minor == 11

def check_dependencies():
    """Lista as dependências instaladas."""
    logger.info("\nDependências instaladas:")
    for pkg in pkg_resources.working_set:
        logger.info(f"{pkg.key} - Version: {pkg.version}")

def main():
    """Verifica o ambiente Python."""
    logger.info("🔍 Verificando ambiente Python...")
    
    if check_python_version():
        logger.info("✅ Versão do Python correta (3.11)")
    else:
        logger.error("❌ Versão do Python incorreta (necessário 3.11)")
    
    check_dependencies()
    logger.info("\n✨ Verificação do ambiente concluída")

if __name__ == "__main__":
    main() 