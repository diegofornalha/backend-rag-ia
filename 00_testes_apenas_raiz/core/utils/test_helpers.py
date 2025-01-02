"""
Utilitários para testes.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from backend_rag_ia.cli.embates.models import Argumento, Embate


def create_test_embate(**overrides: Any) -> Embate:
    """
    Cria um embate para testes com valores padrão.
    
    Args:
        **overrides: Valores para sobrescrever os padrões
        
    Returns:
        Embate configurado para testes
    """
    defaults = {
        "titulo": "Embate de Teste",
        "tipo": "tecnico",
        "contexto": "Contexto para testes",
        "status": "aberto",
        "data_inicio": datetime.now(),
        "argumentos": [
            Argumento(
                autor="Testador",
                conteudo="Argumento de teste",
                tipo="tecnico",
                data=datetime.now()
            )
        ],
        "arquivo": "embate_teste.json",
        "version_key": "embate_teste_v1",
        "error_log": None,
        "metadata": {
            "tags": ["teste"]
        },
        "decisao": None,
        "razao": None
    }
    return Embate(**{**defaults, **overrides})

def create_test_file(embate: Embate, directory: Path) -> Path:
    """
    Cria um arquivo de teste para um embate.
    
    Args:
        embate: Instância de Embate para salvar
        directory: Diretório onde salvar o arquivo
        
    Returns:
        Path do arquivo criado
    """
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / embate.arquivo
    
    with open(file_path, "w") as f:
        json.dump(embate.dict(), f, indent=2, default=str)
    
    return file_path

def create_test_files(embates: list[Embate], directory: Path) -> list[Path]:
    """
    Cria múltiplos arquivos de teste para embates.
    
    Args:
        embates: Lista de embates para salvar
        directory: Diretório onde salvar os arquivos
        
    Returns:
        Lista de Paths dos arquivos criados
    """
    return [create_test_file(embate, directory) for embate in embates]

def cleanup_test_files(directory: Path) -> None:
    """
    Remove arquivos de teste.
    
    Args:
        directory: Diretório para limpar
    """
    if directory.exists():
        for file in directory.glob("embate_*.json"):
            file.unlink()
        
        backup_dir = directory / "backup"
        if backup_dir.exists():
            for file in backup_dir.glob("embate_*.json"):
                file.unlink()
            backup_dir.rmdir()
        
        directory.rmdir()

class MockSupabaseResponse:
    """Mock para respostas do Supabase."""
    
    def __init__(self, data: dict[str, Any]) -> None:
        """
        Inicializa o mock.
        
        Args:
            data: Dados para retornar
        """
        self.data = data
    
    def execute(self) -> "MockSupabaseResponse":
        """Simula execução da query."""
        return self
    
    async def __call__(self) -> dict[str, Any]:
        """Simula chamada assíncrona."""
        return self.data

class MockSupabaseClient:
    """Mock para cliente Supabase."""
    
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        """
        Inicializa o mock.
        
        Args:
            responses: Dicionário de respostas para diferentes RPCs
        """
        self.responses = responses or {}
    
    def rpc(self, function_name: str, params: dict[str, Any] | None = None) -> MockSupabaseResponse:
        """
        Simula chamada RPC.
        
        Args:
            function_name: Nome da função RPC
            params: Parâmetros da chamada
            
        Returns:
            MockSupabaseResponse com dados configurados
        """
        response = MockSupabaseResponse(self.responses.get(function_name, {}))
        return response() 