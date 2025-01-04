"""
Teste de validação de código usando ruff.

Este módulo implementa testes automatizados para verificar:
- Estilo de código (PEP 8)
- Complexidade ciclomática
- Imports não utilizados
- Docstrings
"""

import subprocess
import pytest
from pathlib import Path

def test_ruff_style():
    """Testa se o código está em conformidade com o estilo PEP 8."""
    print("\n=== Teste de Estilo de Código ===")
    
    # Diretórios a serem verificados
    dirs_to_check = [
        "backend_rag_ia",
        "00_testes_apenas_raiz"
    ]
    
    for dir_name in dirs_to_check:
        print(f"\nVerificando diretório: {dir_name}")
        dir_path = Path(dir_name)
        
        if not dir_path.exists():
            print(f"❌ Diretório {dir_name} não encontrado")
            continue
            
        try:
            # Executa ruff check para verificar estilo
            result = subprocess.run(
                ["ruff", "check", dir_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {dir_name}: Nenhum problema de estilo encontrado")
            else:
                print(f"❌ {dir_name}: Problemas de estilo encontrados:")
                print(result.stdout)
                
            assert result.returncode == 0, f"Problemas de estilo encontrados em {dir_name}"
            
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Erro ao executar ruff check: {e}")

def test_ruff_complexity():
    """Testa a complexidade ciclomática do código."""
    print("\n=== Teste de Complexidade de Código ===")
    
    # Configuração do limite de complexidade
    max_complexity = 10
    
    try:
        # Executa ruff com regras de complexidade
        result = subprocess.run(
            [
                "ruff", "check",
                "--select=C901",  # McCabe complexity
                f"--max-complexity={max_complexity}",
                "backend_rag_ia"
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Complexidade dentro do limite aceitável")
        else:
            print("❌ Funções muito complexas encontradas:")
            print(result.stdout)
            
        assert result.returncode == 0, "Código com complexidade acima do limite"
        
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Erro ao verificar complexidade: {e}")

def test_ruff_imports():
    """Testa imports não utilizados e organização de imports."""
    print("\n=== Teste de Imports ===")
    
    try:
        # Verifica imports não utilizados e ordem
        result = subprocess.run(
            [
                "ruff", "check",
                "--select=F401,F403,I",  # Unused imports & import order
                "backend_rag_ia"
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Imports corretamente organizados")
        else:
            print("❌ Problemas com imports encontrados:")
            print(result.stdout)
            
        assert result.returncode == 0, "Problemas com imports encontrados"
        
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Erro ao verificar imports: {e}")

def test_ruff_docstrings():
    """Testa a presença e formato das docstrings."""
    print("\n=== Teste de Docstrings ===")
    
    try:
        # Verifica docstrings
        result = subprocess.run(
            [
                "ruff", "check",
                "--select=D",  # Docstring rules
                "backend_rag_ia"
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Docstrings em conformidade")
        else:
            print("❌ Problemas com docstrings encontrados:")
            print(result.stdout)
            
        assert result.returncode == 0, "Problemas com docstrings encontrados"
        
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Erro ao verificar docstrings: {e}")

if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__]) 