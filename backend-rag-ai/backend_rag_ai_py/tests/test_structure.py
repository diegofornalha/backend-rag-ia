"""
Testes para validar a estrutura do projeto.
"""
import os
import pytest
from pathlib import Path

# Estrutura esperada do projeto
EXPECTED_STRUCTURE = {
    "1_core": ["config", "rules"],
    "2_database": ["migrations", "schemas"],
    "3_deployment": ["docker", "scripts"],
    "4_development": ["docs", "tests"]
}

# Arquivos obrigatórios
REQUIRED_FILES = [
    "1_core/config/environment.py",
    "1_core/rules/REGRAS.md",
    "2_database/schemas/initial_schema.sql",
    "3_deployment/docker/Dockerfile",
    "3_deployment/scripts/deploy.sh"
]

def test_directory_structure():
    """Verifica se a estrutura de diretórios está correta."""
    root = Path("backend-rag-ai")
    
    # Verifica se o diretório raiz existe
    assert root.exists(), f"Diretório raiz {root} não encontrado"
    
    # Verifica cada diretório principal
    for main_dir, subdirs in EXPECTED_STRUCTURE.items():
        main_path = root / main_dir
        assert main_path.exists(), f"Diretório {main_dir} não encontrado"
        assert main_path.is_dir(), f"{main_dir} não é um diretório"
        
        # Verifica subdiretórios
        for subdir in subdirs:
            subdir_path = main_path / subdir
            assert subdir_path.exists(), f"Subdiretório {subdir} não encontrado em {main_dir}"
            assert subdir_path.is_dir(), f"{subdir} em {main_dir} não é um diretório"

def test_required_files():
    """Verifica se todos os arquivos obrigatórios existem."""
    root = Path("backend-rag-ai")
    
    for file_path in REQUIRED_FILES:
        full_path = root / file_path
        assert full_path.exists(), f"Arquivo obrigatório {file_path} não encontrado"
        assert full_path.is_file(), f"{file_path} não é um arquivo"
        
        # Verifica se o arquivo não está vazio
        assert full_path.stat().st_size > 0, f"Arquivo {file_path} está vazio"

def test_no_stray_files():
    """Verifica se não há arquivos soltos na raiz dos diretórios principais."""
    root = Path("backend-rag-ai")
    
    for main_dir in EXPECTED_STRUCTURE.keys():
        main_path = root / main_dir
        
        # Lista todos os arquivos no diretório principal
        files = [f for f in main_path.iterdir() if f.is_file()]
        
        # Verifica se há arquivos soltos
        assert len(files) == 0, f"Arquivos soltos encontrados em {main_dir}: {[f.name for f in files]}"

def test_file_permissions():
    """Verifica as permissões dos arquivos."""
    root = Path("backend-rag-ai")
    
    # Verifica permissões do script de deploy
    deploy_script = root / "3_deployment/scripts/deploy.sh"
    assert deploy_script.exists(), "Script de deploy não encontrado"
    
    # No Unix/Linux, verifica se o script é executável
    if os.name == "posix":
        assert os.access(deploy_script, os.X_OK), "Script de deploy não é executável"

def test_docker_configuration():
    """Verifica a configuração do Docker."""
    root = Path("backend-rag-ai")
    dockerfile = root / "3_deployment/docker/Dockerfile"
    
    assert dockerfile.exists(), "Dockerfile não encontrado"
    
    # Lê o conteúdo do Dockerfile
    content = dockerfile.read_text()
    
    # Verifica elementos essenciais
    assert "FROM" in content, "Dockerfile não tem instrução FROM"
    assert "HEALTHCHECK" in content, "Dockerfile não tem HEALTHCHECK configurado"
    assert "USER" in content, "Dockerfile não configura usuário não-root"

def test_database_schema():
    """Verifica o schema do banco de dados."""
    root = Path("backend-rag-ai")
    schema_file = root / "2_database/schemas/initial_schema.sql"
    
    assert schema_file.exists(), "Arquivo de schema não encontrado"
    
    # Lê o conteúdo do schema
    content = schema_file.read_text().upper()
    
    # Verifica elementos essenciais
    assert "CREATE TABLE" in content, "Schema não tem definição de tabelas"
    assert "CREATE INDEX" in content, "Schema não tem definição de índices"
    assert "CREATE FUNCTION" in content, "Schema não tem definição de funções" 