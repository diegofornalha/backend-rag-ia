import os
import pkg_resources
import pytest


def test_required_packages():
    """Testa se os pacotes necessários estão instalados"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pytest",
        "langchain",
        "supabase",
        "rich",
        "requests",
    ]

    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

    for package in required_packages:
        assert package in installed_packages, f"Pacote {package} não está instalado"


def test_requirements_file():
    """Testa se o arquivo requirements.txt existe e é válido"""
    req_file = "requirements.txt"
    assert os.path.exists(req_file), "requirements.txt não encontrado"

    with open(req_file) as f:
        content = f.read()
        assert content.strip(), "requirements.txt está vazio"

    # Verifica se pode ser parseado
    try:
        pkg_resources.parse_requirements(content)
    except Exception as e:
        pytest.fail(f"requirements.txt inválido: {e}")


def test_virtual_environment():
    """Testa se está rodando em um ambiente virtual"""
    venv_path = os.environ.get("VIRTUAL_ENV")
    
    if not venv_path and not os.environ.get("CI"):  # Ignora em CI
        pytest.fail("Não está rodando em um ambiente virtual")
    
    if venv_path:
        assert os.path.exists(venv_path), "Caminho do ambiente virtual não existe" 