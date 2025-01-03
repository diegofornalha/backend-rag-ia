"""
Configuração global para testes.
"""

import asyncio
import os
import shutil
from collections.abc import Generator
from pathlib import Path

import pytest

# Configuração de ambiente para testes
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["SUPABASE_JWT"] = "test-jwt"

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Cria um event loop para testes assíncronos.
    
    Yields:
        Event loop para testes
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_root() -> Path:
    """
    Retorna o diretório raiz para testes.
    
    Returns:
        Path do diretório raiz
    """
    return Path(__file__).parent

@pytest.fixture(scope="session")
def test_data_dir(test_root: Path) -> Path:
    """
    Retorna o diretório de dados de teste.
    
    Args:
        test_root: Diretório raiz dos testes
        
    Returns:
        Path do diretório de dados
    """
    return test_root / "fixtures"

@pytest.fixture(autouse=True)
def cleanup_test_files(request):
    """
    Limpa arquivos de teste após cada teste.
    
    Args:
        request: Fixture request do pytest
    """
    yield
    
    # Limpa diretórios temporários
    temp_dirs = [
        "test_embates",
        "test_embates_integration"
    ]
    
    for dir_name in temp_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path) 