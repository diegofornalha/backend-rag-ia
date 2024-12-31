import os
import shutil
import sys

import pytest


def test_python_version():
    """Testa a versão do Python"""
    version = sys.version_info
    assert version.major == 3, "Python major version deve ser 3"
    assert version.minor >= 11, "Python minor version deve ser >= 11"


def test_python_executable():
    """Testa o executável Python"""
    executable = sys.executable
    assert os.path.exists(executable), "Executável Python não encontrado"
    assert os.access(executable, os.X_OK), "Executável Python sem permissão de execução"


def test_environment_variables():
    """Testa variáveis de ambiente críticas"""
    critical_vars = [
        "PYTHONPATH",
        "VIRTUAL_ENV",
        "SUPABASE_URL",
        "SUPABASE_KEY",
    ]

    for var in critical_vars:
        if not os.environ.get(var):
            pytest.skip(f"Variável de ambiente {var} não definida")


def test_disk_space():
    """Testa espaço em disco disponível"""
    # Verifica espaço no diretório atual
    total, used, free = shutil.disk_usage(".")
    
    # Converte para GB
    free_gb = free // (2**30)
    
    # Deve ter pelo menos 1GB livre
    assert free_gb >= 1, f"Espaço em disco insuficiente. Livre: {free_gb}GB"


def test_network_connectivity():
    """Testa conectividade básica de rede"""
    try:
        # Testa DNS
        import socket
        socket.gethostbyname("google.com")
        
        # Testa HTTP
        import urllib.request
        response = urllib.request.urlopen("https://api.render.com", timeout=5)
        assert response.getcode() == 200, "Falha ao conectar com Render API"
    except Exception as e:
        pytest.fail(f"Erro de conectividade: {e}") 