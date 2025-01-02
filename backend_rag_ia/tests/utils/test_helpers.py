"""
Helpers para testes.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

from ...cli.embates.models import Argumento, Embate

class MockSupabaseClient:
    """Mock do cliente Supabase."""
    
    def __init__(self):
        self.data = []
        self.table = MagicMock()
        self.table.insert = AsyncMock(return_value=self)
        self.table.select = AsyncMock(return_value=self)
        self.table.eq = AsyncMock(return_value=self)
        self.execute = AsyncMock(return_value=self)
        
    def set_data(self, data: List[Dict]) -> None:
        """Define dados para retornar."""
        self.data = data

def create_test_embate(
    titulo: str = "Teste",
    tipo: str = "tecnico",
    contexto: str = "Contexto de teste",
    status: str = "aberto",
    metadata: Optional[Dict] = None,
    argumentos: Optional[List[Argumento]] = None,
    id: Optional[str] = None
) -> Embate:
    """
    Cria um embate para teste.
    
    Args:
        titulo: Título do embate
        tipo: Tipo do embate
        contexto: Contexto do embate
        status: Status do embate
        metadata: Metadata opcional
        argumentos: Argumentos opcionais
        id: ID opcional
        
    Returns:
        Embate criado
    """
    return Embate(
        titulo=titulo,
        tipo=tipo,
        contexto=contexto,
        status=status,
        metadata=metadata or {},
        argumentos=argumentos or [],
        criado_em=datetime.now(),
        atualizado_em=datetime.now(),
        id=id
    )

def create_test_argumento(
    nome: str = "arg_teste",
    valor: str = "valor_teste",
    tipo: str = "texto",
    descricao: Optional[str] = None
) -> Argumento:
    """
    Cria um argumento para teste.
    
    Args:
        nome: Nome do argumento
        valor: Valor do argumento
        tipo: Tipo do argumento
        descricao: Descrição opcional
        
    Returns:
        Argumento criado
    """
    return Argumento(
        nome=nome,
        valor=valor,
        tipo=tipo,
        descricao=descricao
    )

def create_test_file(embate: Embate, directory: Path) -> Path:
    """
    Cria um arquivo de teste para um embate.
    
    Args:
        embate: Embate para salvar
        directory: Diretório onde salvar
        
    Returns:
        Path do arquivo criado
    """
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / f"embate_{embate.id}.json"
    
    with open(file_path, "w") as f:
        json.dump(embate.dict(), f, indent=2, default=str)
        
    return file_path

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