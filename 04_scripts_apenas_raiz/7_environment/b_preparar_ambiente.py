#!/usr/bin/env python3
import subprocess
import sys
import os
import logging
from pathlib import Path

# Configurando logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_python_version():
    """Verifica se estamos usando Python 3.11."""
    version = sys.version_info
    if version.major == 3 and version.minor == 11:
        logger.info("✅ Python 3.11 já está em uso")
        return True
    logger.error(f"❌ Python {version.major}.{version.minor} detectado. Necessário Python 3.11")
    return False

def create_virtual_env():
    """Cria um ambiente virtual com Python 3.11."""
    try:
        venv_path = Path(".venv")
        if venv_path.exists():
            logger.info("🗑️ Removendo ambiente virtual antigo...")
            subprocess.run(["rm", "-rf", str(venv_path)], check=True)
        
        logger.info("🔧 Criando novo ambiente virtual com Python 3.11...")
        subprocess.run(["python3.11", "-m", "venv", ".venv"], check=True)
        logger.info("✅ Ambiente virtual criado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao criar ambiente virtual: {e}")
        return False
    except FileNotFoundError:
        logger.error("❌ Python 3.11 não encontrado. Por favor, instale-o primeiro")
        return False

def install_dependencies():
    """Instala as dependências com versões específicas."""
    try:
        logger.info("📦 Instalando dependências...")
        subprocess.run([".venv/bin/pip", "install", "-U", "pip"], check=True)
        
        dependencies = [
            "sentence-transformers==2.2.2",
            "torch==2.0.1",
            "transformers==4.30.2",
            "huggingface-hub==0.16.4",
            "supabase==1.0.3",
            "rich==13.4.2",
            "python-dotenv==1.0.0",
            "numpy==1.24.3",
            "fastapi==0.104.1",
            "uvicorn==0.24.0",
            "ruff==0.1.6"
        ]
        
        for dep in dependencies:
            logger.info(f"📥 Instalando {dep}...")
            subprocess.run([".venv/bin/pip", "install", dep], check=True)
        
        logger.info("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao instalar dependências: {e}")
        return False

def main():
    """Prepara o ambiente de desenvolvimento."""
    logger.info("🚀 Iniciando preparação do ambiente...")
    
    if not check_python_version():
        if not create_virtual_env():
            logger.error("⚠️ Falha ao criar ambiente virtual")
            return
    
    if install_dependencies():
        logger.info("""
✨ Ambiente preparado com sucesso!

Para ativar o ambiente:
  source .venv/bin/activate

Para verificar a instalação:
  python scripts_apenas_raiz/verificar_ambiente.py
""")
    else:
        logger.error("⚠️ Falha ao preparar o ambiente")

if __name__ == "__main__":
    main() 